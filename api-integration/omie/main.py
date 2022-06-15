import base64
import json
from pprint import pprint

import requests
from google.cloud import bigquery

import schema
from dto import MovimentosFinanceiros, CategoriasCadastro, ClientesCadastro
from dto.ClientesCadastro import ClientesListRequest, ClientesPorCodigo
from dto.MovimentosFinanceiros import MfListarRequest
from schema import partition_field, bigquery_formatter
from utils.bigqueryutil import create_table_if_not_exists, insert_rows_bq

SOURCE_DATE_FORMAT = '%d/%m/%Y'
BIGQUERY_DATE_FORMAT = '%Y-%m-%d'

client = bigquery.Client()


#
# def compare_department(
#     dd: DepartamentoCadastro.departamento,
#     md: MovimentosFinanceiros.Departamento
# ):
#     return dd['codigo'] == md['cCodDepartamento']


def hello(event, context):
    parameters = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    try:
        # resp = MovimentosFinanceiros.listar_movimentos(
        #     MfListarRequest(dDtPagtoDe='01/01/2022', cStatus='LIQUIDADO'))
        request_body = MfListarRequest(dDtPagtoDe='01/06/2022',
                                       nRegPorPagina=100,
                                       cStatus='LIQUIDADO')
        resp = MovimentosFinanceiros.get(request_body, bigquery_formatter)

        table_id = parameters["tableId"]
        dataset_id = parameters['datasetId']
        project_id = parameters['projectId']

        categories: CategoriasCadastro.get()

        client_id_array = list(
            map(lambda c: ClientesPorCodigo(codigo_cliente_omie=c),
                map(lambda m: m["detalhes"]["nCodCliente"], resp)))
        clients = ClientesCadastro.get(
            ClientesListRequest(
                clientesPorCodigo=client_id_array))

        def bq_builder(m: MovimentosFinanceiros.Movimento):
            schema.builder(m, clients, categories)

        bigquery_rows = list(map(bq_builder, resp))
        pprint(bigquery_rows[0])

        create_table_if_not_exists(client, table_id, dataset_id, project_id,
                                   schema.movimentos_schema,
                                   partition_field)
        insert_rows_bq(client, table_id, dataset_id, project_id,
                       bigquery_rows)

    except requests.exceptions.RequestException as e:
        return e
