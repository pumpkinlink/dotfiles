import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict

from dateutil import parser as date_parser
from google.cloud import bigquery
from google.cloud.functions_v1.context import Context

import schema
from dto import MovimentosFinanceiros, CategoriasCadastro, ClientesCadastro, \
    BQMovement, ContaCorrenteCadastro, DepartamentosCadastro, \
    ProjetosCadastro
from dto.BQMovement import partition_field, bigquery_formatter, \
    OMIE_DATE_FORMAT, ISO_DATE_FORMAT
from dto.ClientesCadastro import ClientesListRequest, ClientesPorCodigo
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse, \
    Movimento
from utils import OmiePaginator
from utils.bigqueryutil import create_table_if_not_exists, insert_rows_bq, \
    merge_rows_bq

client = bigquery.Client()
debug = os.environ.get("DEBUG") == "1"
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class Attributes(TypedDict, total=False):
    tableId: str
    tempTableId: str
    datasetId: str
    projectId: str
    startDate: str
    isInitialLoad: str


@dataclass
class StarSchemaTables:
    categories: list[CategoriasCadastro]
    departments: list[DepartamentosCadastro]
    checking_accounts: list[ContaCorrenteCadastro]
    projects: list[ProjetosCadastro]


def migrate(event: dict, context: Context):
    attributes: Attributes = event['attributes']
    start_date = attributes['startDate']
    end_date = format(
        date_parser.parse(context.timestamp).date(),
        OMIE_DATE_FORMAT
    )
    request_body = MfListarRequest(dDtPagtoDe=start_date,
                                   dDtPagtoAte=end_date,
                                   nRegPorPagina=500,
                                   cStatus='LIQUIDADO')
    paginator = MovimentosFinanceiros.get_paginator(request=request_body,
                                                    object_hook=bigquery_formatter)

    table_id = attributes["tableId"]
    dataset_ref = f"{attributes['projectId']}.{attributes['datasetId']}"

    categories = CategoriasCadastro.get_all()
    departments = DepartamentosCadastro.get_all()
    checking_accounts = ContaCorrenteCadastro.get_all()
    projects = ProjetosCadastro.get_all()

    create_table_if_not_exists(client=client,
                               table_id=table_id,
                               dataset_ref=dataset_ref,
                               schema=schema.movimentos_schema,
                               partitioning_field=partition_field)

    if attributes["isInitialLoad"] == 'True':
        insert_by_page(
            StarSchemaTables(categories, departments, checking_accounts,
                             projects),
            dataset_ref=dataset_ref,
            table_id=table_id,
            paginator=paginator
        )
    else:
        update_table(
            StarSchemaTables(categories, departments, checking_accounts,
                             projects),
            dataset_ref=dataset_ref,
            table_id=table_id,
            temp_table_id=attributes['tempTableId'],
            paginator=paginator
        )


def update_table(
    star_tables: StarSchemaTables,
    dataset_ref: str,
    table_id: str,
    temp_table_id: str,
    paginator: OmiePaginator
):
    movements = paginator.concat_all_pages()
    logging.info('buscando clientes...')
    clients = get_clients(movements)

    bigquery_rows = convert_to_schema_rows(movements=movements,
                                           clients_to_search=clients,
                                           star_tables=star_tables)
    logging.info(f'Escrevendo {len(bigquery_rows)} linhas no banco...')
    bq_errors = merge_rows_bq(
        client=client,
        table_id=table_id,
        temp_table_id=temp_table_id,
        dataset_ref=dataset_ref,
        data=bigquery_rows
    )
    logging.info(f'Escreveu {len(bigquery_rows)} linhas com sucesso!')
    handle_bq_errors(bq_errors)


def insert_by_page(
    star_tables: StarSchemaTables,
    dataset_ref: str,
    table_id: str,
    paginator: OmiePaginator
):
    pages = [paginator.get_page(1)]

    def append_page(number: int, pages_):
        logging.info(f'Requisitando página {page_number + 1}')
        pages_.append(paginator.get_page(number))
        logging.info(f'Recebeu página {number}')

    for page_number in range(1, paginator.total_pages + 1):
        get_next_page = threading.Thread(
            target=append_page, args=[page_number + 1, pages])
        get_next_page.start()

        page: MfListarResponse = pages[page_number - 1]
        resp = page['movimentos']
        logging.info(f'buscando clientes página {page_number}')
        clients = get_clients(resp)

        bigquery_rows = convert_to_schema_rows(movements=resp,
                                               clients_to_search=clients,
                                               star_tables=star_tables)

        logging.info(f'Escrevendo página {page_number} no banco...')
        bq_errors = insert_rows_bq(client=client,
                                   table_id=table_id,
                                   dataset_ref=dataset_ref,
                                   data=bigquery_rows)
        handle_bq_errors(bq_errors)
        message = f'Escreveu página {page_number}, {len(bigquery_rows)}' \
                  f' linhas inseridas com sucesso!'
        get_next_page.join()
        logging.info(message)


def convert_to_schema_rows(
    movements,
    clients_to_search: list[ClientesCadastro],
    star_tables: StarSchemaTables
):
    def bq_builder(m: MovimentosFinanceiros.Movimento):
        return BQMovement.build(m,
                                clients_to_search,
                                star_tables.categories,
                                star_tables.departments,
                                star_tables.checking_accounts,
                                star_tables.projects)

    bigquery_rows = list(map(bq_builder, movements))
    if len(bigquery_rows) != len(movements):
        message = f'Erro na conversão: api {len(movements)} linhas, convertido {len(bigquery_rows)} linhas.'
        logging.error(message)
        raise Exception(message)
    return bigquery_rows


def get_clients(movements: list[Movimento]):
    int_array = list(
        set(map(lambda m: m["detalhes"]["nCodCliente"], movements)))
    client_filter_array = list(
        map(lambda c: ClientesPorCodigo(codigo_cliente_omie=c),
            int_array))
    return ClientesCadastro.get(
        ClientesListRequest(clientesPorCodigo=client_filter_array))


def handle_bq_errors(bq_errors):
    if bq_errors is not None:
        message = f'{len(bq_errors)} erros, primeiro erro: ->> {vars(bq_errors[0])} <<- .'
        logging.error(message)
        raise Exception(message)


if debug:
    migrate(
        {
            "attributes": {
                "tableId": "movimentos",
                "datasetId": "ideamaker_raw_financial",
                "projectId": "idea-data-homol",
                "startDate": '01/01/2022',
                "isInitialLoad": 'True'
            }
        },
        Context(timestamp=format(
            datetime.now() - timedelta(days=1),
            ISO_DATE_FORMAT)
        )
        # Context(timestamp='2022-01-01')
    )
