import logging
import os
import threading
from datetime import datetime, timedelta

from dateutil import parser
from google.cloud import bigquery
from google.cloud.functions_v1.context import Context

import schema
from dto import MovimentosFinanceiros, CategoriasCadastro, ClientesCadastro, \
    BQMovement, ContaCorrenteCadastro, DepartamentosCadastro, \
    ProjetosCadastro
from dto.BQMovement import partition_field, bigquery_formatter, OMIE_DATE_FORMAT
from dto.ClientesCadastro import ClientesListRequest, ClientesPorCodigo
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse
from utils.bigqueryutil import create_table_if_not_exists, insert_rows_bq

client = bigquery.Client()
debug = os.environ.get("DEBUG") == "1"
logging.basicConfig(level=logging.INFO)


def migrate(event: dict, context: Context):
    atributes = event['attributes']
    start_date = atributes['startDate']
    end_date = parser.parse(context.timestamp).date() - timedelta(days=1)

    request_body = MfListarRequest(dDtPagtoDe=start_date,
                                   dDtPagtoAte=format(end_date,
                                                      OMIE_DATE_FORMAT),
                                   nRegPorPagina=500,
                                   cStatus='LIQUIDADO')
    paginator = MovimentosFinanceiros.get_paginator(request=request_body,
                                                    object_hook=bigquery_formatter)
    total_pages = paginator.total_pages
    # resp = mock.resp

    table_id = atributes["tableId"]
    dataset_id = atributes['datasetId']
    project_id = atributes['projectId']

    categories = CategoriasCadastro.get_all()
    departments = DepartamentosCadastro.get_all()
    checking_accounts = ContaCorrenteCadastro.get_all()
    projects = ProjetosCadastro.get_all()

    create_table_if_not_exists(client, table_id, dataset_id, project_id,
                               schema.movimentos_schema,
                               partition_field)

    logging.info(f'Requisitando página 1')
    pages = [paginator.get_page(1)]

    def append_page(number: int, pages_):
        logging.info(f'Requisitando página {page_number + 1}')
        pages_.append(paginator.get_page(number))
        logging.info(f'Recebeu página {number}')

    for page_number in range(1, total_pages + 1):
        get_next_page = threading.Thread(
            target=append_page, args=[page_number + 1, pages])
        get_next_page.start()

        page: MfListarResponse = pages[page_number - 1]
        resp = page['movimentos']
        int_array = list(set(map(lambda m: m["detalhes"]["nCodCliente"], resp)))
        client_filter_array = list(
            map(lambda c: ClientesPorCodigo(codigo_cliente_omie=c),
                int_array))

        logging.info(f'buscando clientes página {page_number}')
        clients = ClientesCadastro.get(
            ClientesListRequest(clientesPorCodigo=client_filter_array))

        def bq_builder(m: MovimentosFinanceiros.Movimento):
            return BQMovement.build(m, clients, categories, departments,
                                    checking_accounts, projects)

        bigquery_rows = list(map(bq_builder, resp))
        if len(bigquery_rows) != len(resp):
            message = f'Erro na conversão: api {len(resp)} linhas, convertido {len(bigquery_rows)} linhas.'
            logging.error(message)
            raise Exception(message)

        logging.info(f'Escrevendo página {page_number} no banco...')
        bq_errors = insert_rows_bq(client, table_id, dataset_id,
                                   project_id,
                                   data=bigquery_rows)
        if bq_errors is not None:
            message = f'{len(bq_errors)} erros, primeiro erro: ->> {vars(bq_errors[0])} <<- .'
            logging.error(message)
            raise Exception(message)
        message = f'Escreveu página {page_number}, {len(bigquery_rows)}' \
                  f' linhas inseridas com sucesso!'
        get_next_page.join()
        logging.info(message)


if debug:
    migrate(
        {
            "attributes": {
                "tableId": "movimentos",
                "datasetId": "dataset",
                "projectId": "idea-data-homol",
                "startDate": '01/01/1901'
            }
        },
        Context(timestamp=format(datetime.now(), OMIE_DATE_FORMAT))
    )
