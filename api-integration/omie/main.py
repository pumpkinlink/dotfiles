import base64
import json
import os

from google.cloud import bigquery

import schema
from dto import MovimentosFinanceiros, CategoriasCadastro, ClientesCadastro, \
    BQMovement, ContaCorrenteCadastro, DepartamentosCadastro, \
    ProjetosCadastro
from dto.BQMovement import partition_field, bigquery_formatter
from dto.ClientesCadastro import ClientesListRequest, ClientesPorCodigo
from dto.MovimentosFinanceiros import MfListarRequest
from utils.bigqueryutil import create_table_if_not_exists, insert_rows_bq

client = bigquery.Client()
debug = os.environ.get("DEBUG") == "1"


def migrate(event, context):
    if debug:
        parameters = {
            "tableId": "movimentos",
            "datasetId": "dataset",
            "projectId": "idea-data-homol"
        }
    else:
        parameters = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    request_body = MfListarRequest(dDtPagtoDe='01/07/2017',
                                   nRegPorPagina=500,
                                   cStatus='LIQUIDADO')
    resp = MovimentosFinanceiros.get(request_body, bigquery_formatter)

    table_id = parameters["tableId"]
    dataset_id = parameters['datasetId']
    project_id = parameters['projectId']

    categories = CategoriasCadastro.get_all()
    departments = DepartamentosCadastro.get_all()
    checking_accounts = ContaCorrenteCadastro.get_all()
    projects = ProjetosCadastro.get_all()

    int_array = list(set(map(lambda m: m["detalhes"]["nCodCliente"], resp)))
    client_filter_array = list(
        map(lambda c: ClientesPorCodigo(codigo_cliente_omie=c),
            int_array))
    clients = ClientesCadastro.get(
        ClientesListRequest(
            clientesPorCodigo=client_filter_array))

    def bq_builder(m: MovimentosFinanceiros.Movimento):
        return BQMovement.build(m, clients, categories, departments,
                                checking_accounts, projects)

    bigquery_rows = list(map(bq_builder, resp))
    if len(bigquery_rows) != len(resp):
        return f'Erro na conversão: api {len(resp)} linhas, convertido {len(bigquery_rows)} linhas.'

    create_table_if_not_exists(client, table_id, dataset_id, project_id,
                               schema.movimentos_schema,
                               partition_field)
    bq_errors = insert_rows_bq(client, table_id, dataset_id, project_id,
                               bigquery_rows)
    if len(bq_errors) > 0:
        message = f'{len(bq_errors)} erros, primeiro erro: ->> {vars(bq_errors[0])} <<- .'
        return message, 500
    return f'{len(bigquery_rows)} linhas inseridas com sucesso!', 200


if debug:
    migrate(None, None)
