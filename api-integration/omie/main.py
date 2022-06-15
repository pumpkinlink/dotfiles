import base64
import json
from pprint import pprint

import requests
from google.cloud import bigquery

from dto import MovimentosFinanceiros, CategoriasCadastro, ClientesCadastro, \
    BQMovement, ContaCorrenteCadastro, DepartamentosCadastro, ProjetosCadastro
from dto.BQMovement import bigquery_formatter
from dto.ClientesCadastro import ClientesListRequest, ClientesPorCodigo
from dto.MovimentosFinanceiros import MfListarRequest

client = bigquery.Client()


def hello(event, context):
    parameters = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    try:
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
        pprint(len(bigquery_rows))

        # create_table_if_not_exists(client, table_id, dataset_id, project_id,
        #                            schema.movimentos_schema,
        #                            partition_field)
        # insert_rows_bq(client, table_id, dataset_id, project_id,
        #                bigquery_rows)

    except requests.exceptions.RequestException as e:
        return e
