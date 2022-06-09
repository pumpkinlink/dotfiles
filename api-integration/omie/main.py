import base64
import datetime
import json
import re
from http import HTTPStatus
from pprint import pprint

import functions_framework
import requests
from flask import Request, Response
from google.cloud import bigquery

from pandas import DataFrame

import schema
from schema import partition_field
from bigqueryutil import create_table_if_not_exists, insert_rows_bq
from dto import MovimentosFinanceiros
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse, \
    Movimento

SOURCE_DATE_FORMAT = '%d/%m/%Y'
BIGQUERY_DATE_FORMAT = '%Y-%m-%d'


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and re.search("^dDt", k):
            dct[k] = datetime.datetime.strptime(v,
                                                SOURCE_DATE_FORMAT).date().strftime(
                BIGQUERY_DATE_FORMAT)
        elif isinstance(v, float) and k in [
            'nValorTitulo',
            'nValorPIS',
            'nValorCOFINS',
            'nValorCSLL',
            'nValorIR',
            'nValorISS',
            'nValorINSS',
            'nValorMovCC',

            'nValPago',
            'nValAberto',
            'nDesconto',
            'nJuros',
            'nMulta',
            'nValLiquido',

            'nDistrPercentual',
            'nDistrValor'
        ]:
            dct[k] = str(v)
    return dct


def convert_to_schema(m: Movimento):
    row = {
        **m['detalhes'],
        **m['resumo'],
        "departamentos": m["departamentos"] if 'departamentos' in m else [],
        "categorias": m["categorias"] if 'categorias' in m else []
    }
    return row


client = bigquery.Client()


def hello(event, context):
    parameters = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    try:
        resp = MovimentosFinanceiros.listar_movimentos(
            MfListarRequest(dDtPagtoDe='01/01/2022', cStatus='LIQUIDADO'))

        if 200 <= resp.status_code < 300:
            response_body: MfListarResponse = json.loads(resp.content,
                                                         object_hook=datetime_parser)
            # pprint(response_body)
            print("Movimentos -> ")
            pprint(
                {x: response_body[x] for x in response_body if x != 'movimentos'}
            )

            table_id = parameters["tableId"]
            dataset_id = parameters['datasetId']
            project_id = parameters['projectId']

            bigquery_rows = list(
                map(convert_to_schema, response_body['movimentos']))
            # pprint(bigquery_rows)
            create_table_if_not_exists(client, table_id, dataset_id, project_id,
                                       schema.movimentos_schema,
                                       partition_field)
            insert_rows_bq(client, table_id, dataset_id, project_id,
                           bigquery_rows)
            # dataframe = DataFrame.from_records(response_body['movimentos'])

            return response_body['nRegistros']
        else:
            return resp.status_code

    except requests.exceptions.RequestException as e:
        return e
