import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import TypedDict

from dateutil import parser as date_parser
from google.cloud import bigquery
from google.cloud.functions_v1.context import Context

import schema
from dto import (
    movimentos_financeiros,
    categorias,
    clientes,
    contas_correntes,
    departamentos,
    projetos,
    bq_movement,
)
from dto.bq_movement import partition_field, bigquery_formatter, OMIE_DATE_FORMAT
from dto.clientes import ClientesListRequest, ClientesPorCodigo
from dto.movimentos_financeiros import MfListarRequest, MfListarResponse, Movimento
from utils.big_query_util import (
    create_table_if_not_exists,
    insert_rows_bq,
    merge_rows_bq,
)
from utils.omie_paginator import PaginatorCamelCase

client = bigquery.Client()
debug = os.environ.get("DEBUG") == "1"
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Attributes(TypedDict, total=False):
    """
    map (key: string, value: string)
    Attributes for this message. If this field is empty, the message must contain non-empty data. This can be used to filter messages on the subscription.

    An object containing a list of "key": value pairs. Example: { "name": "wrench", "mass": "1.3kg", "count": "3" }.
    """

    tableId: str
    tempTableId: str
    datasetId: str
    projectId: str
    daysInterval: str
    isInitialLoad: str


@dataclass
class StarSchemaTables:
    categories: list[categorias]
    departments: list[departamentos]
    checking_accounts: list[contas_correntes]
    projects: list[projetos]


def migrate(event: dict, context: Context):
    attributes: Attributes = event["attributes"]
    end_date = date_parser.parse(context.timestamp).date()
    start_date = end_date - timedelta(days=int(attributes["daysInterval"]))
    start_date_br = format(start_date, OMIE_DATE_FORMAT)
    end_date_br = format(end_date, OMIE_DATE_FORMAT)
    request_body = MfListarRequest(
        dDtPagtoDe=start_date_br,
        dDtPagtoAte=end_date_br,
        nRegPorPagina=500,
        cStatus="LIQUIDADO",
    )
    paginator = movimentos_financeiros.get_paginator(
        request=request_body, object_hook=bigquery_formatter
    )

    table_id = attributes["tableId"]
    dataset_ref = f"{attributes['projectId']}.{attributes['datasetId']}"

    categories = categorias.get_all()
    departments = departamentos.get_all()
    checking_accounts = contas_correntes.get_all()
    projects = projetos.get_all()

    create_table_if_not_exists(
        client=client,
        table_id=table_id,
        dataset_ref=dataset_ref,
        schema=schema.movimentos_schema,
        partitioning_field=partition_field,
    )

    if attributes["isInitialLoad"] == "True":
        insert_by_page(
            StarSchemaTables(categories, departments, checking_accounts, projects),
            dataset_ref=dataset_ref,
            table_id=table_id,
            paginator=paginator,
        )
    else:
        update_table(
            StarSchemaTables(categories, departments, checking_accounts, projects),
            dataset_ref=dataset_ref,
            table_id=table_id,
            temp_table_id=attributes["tempTableId"],
            paginator=paginator,
            start_date=start_date,
        )


def update_table(
    star_tables: StarSchemaTables,
    dataset_ref: str,
    table_id: str,
    temp_table_id: str,
    paginator: PaginatorCamelCase,
    start_date: date,
):
    movements = paginator.concat_all_pages()
    logging.info("buscando clientes...")
    clients = get_clients(movements)

    bigquery_rows = convert_to_schema_rows(
        movements=movements, clients_to_search=clients, star_tables=star_tables
    )
    logging.info(f"Escrevendo {len(bigquery_rows)} linhas no banco...")
    bq_errors = merge_rows_bq(
        client=client,
        table_id=table_id,
        temp_table_id=temp_table_id,
        dataset_ref=dataset_ref,
        data=bigquery_rows,
        start_date=start_date,
    )
    logging.info(f"Escreveu {len(bigquery_rows)} linhas com sucesso!")
    handle_bq_errors(bq_errors)


def insert_by_page(
    star_tables: StarSchemaTables,
    dataset_ref: str,
    table_id: str,
    paginator: PaginatorCamelCase,
):
    pages = [paginator.get_page(1)]

    def append_page(number: int, pages_):
        logging.info(f"Requisitando página {page_number + 1}")
        pages_.append(paginator.get_page(number))
        logging.info(f"Recebeu página {number}")

    for page_number in range(1, paginator.total_pages + 1):
        get_next_page = threading.Thread(
            target=append_page, args=[page_number + 1, pages]
        )
        get_next_page.start()

        # noinspection PyTypeChecker
        page: MfListarResponse = pages[page_number - 1]
        resp = page["movimentos"]
        logging.info(f"buscando clientes página {page_number}")
        clients = get_clients(resp)

        bigquery_rows = convert_to_schema_rows(
            movements=resp, clients_to_search=clients, star_tables=star_tables
        )

        logging.info(f"Escrevendo página {page_number} no banco...")
        bq_errors = insert_rows_bq(
            client=client,
            table_id=table_id,
            dataset_ref=dataset_ref,
            data=bigquery_rows,
        )
        handle_bq_errors(bq_errors)
        message = (
            f"Escreveu página {page_number}, {len(bigquery_rows)}"
            f" linhas inseridas com sucesso!"
        )
        get_next_page.join()
        logging.info(message)


def convert_to_schema_rows(
    movements, clients_to_search: list[clientes], star_tables: StarSchemaTables
):
    def bq_builder(m: movimentos_financeiros.Movimento):
        return bq_movement.build(
            m,
            clients_to_search,
            star_tables.categories,
            star_tables.departments,
            star_tables.checking_accounts,
            star_tables.projects,
        )

    bigquery_rows = list(map(bq_builder, movements))
    if len(bigquery_rows) != len(movements):
        message = f"Erro na conversão: api {len(movements)} linhas, convertido {len(bigquery_rows)} linhas."
        logging.error(message)
        raise Exception(message)
    return bigquery_rows


def get_clients(movements: list[Movimento]):
    int_array = list(set(map(lambda m: m["detalhes"]["nCodCliente"], movements)))
    client_filter_array = list(
        map(lambda c: ClientesPorCodigo(codigo_cliente_omie=c), int_array)
    )
    return clientes.get(ClientesListRequest(clientesPorCodigo=client_filter_array))


def handle_bq_errors(bq_errors):
    if bq_errors is not None:
        message = (
            f"{len(bq_errors)} erros, primeiro erro: ->> {vars(bq_errors[0])} <<- ."
        )
        logging.error(message)
        raise Exception(message)


if debug:
    migrate(
        {
            "attributes": {
                "tableId": "movimentos",
                "datasetId": "ideamaker_raw_financial",
                "projectId": "idea-data-homol",
                "startDate": "2022-01-01",
                "isInitialLoad": "True",
            }
        },
        Context(timestamp=(datetime.now() - timedelta(days=1)).isoformat())
        # Context(timestamp='2022-01-01')
    )
