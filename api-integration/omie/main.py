import base64
import datetime
import json
import re
from pprint import pprint

import requests
from google.cloud import bigquery

import schema
from dto.CategoriasCadastro import CategoriaCadastro, CategoriaListRequest
from schema import partition_field
from utils.OmiePaginator import PaginatorCamelCase, PaginatorSlugCase
from utils.bigqueryutil import create_table_if_not_exists, insert_rows_bq
from dto import MovimentosFinanceiros, CategoriasCadastro
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse, \
    Movimento

SOURCE_DATE_FORMAT = '%d/%m/%Y'
BIGQUERY_DATE_FORMAT = '%Y-%m-%d'


def bigquery_formatter(dct):
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


def spread_to_schema(m: Movimento):
    row = {
        **m['detalhes'],
        **m['resumo'],
        "departamentos": m["departamentos"] if 'departamentos' in m else [],
        "categorias": m["categorias"] if 'categorias' in m else []
    }
    return row


client = bigquery.Client()


def compare_array_category(
    cc: CategoriasCadastro.CategoriaCadastro,
    mc: MovimentosFinanceiros.Categoria
):
    return cc['codigo'] == mc['cCodCateg']


def compare_category(
    cc: CategoriasCadastro.CategoriaCadastro,
    code: str
):
    return cc['codigo'] == code


def set_categories(movement, categories: list):
    if movement["cCodCateg"] is not None:
        result: list[CategoriasCadastro.CategoriaCadastro] = list(
            filter(
                lambda cc: compare_category(cc=cc, code=movement["cCodCateg"]),
                categories))
        movement['descricao_categoria'] = result[0]['descricao'] if len(
            result) > 0 else None

    for mc in movement["categorias"]:
        result: list[CategoriasCadastro.CategoriaCadastro] = list(
            filter(lambda cc: compare_array_category(cc=cc, mc=mc), categories))
        mc['descricao_categoria'] = result[0]['descricao'] if len(
            result) > 0 else None
    return movement


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
        movimento_paginator = PaginatorCamelCase(
            request_body,
            MovimentosFinanceiros.poster,
            bigquery_formatter, MovimentosFinanceiros.page_body_key)
        resp: list[Movimento] = movimento_paginator.concat_all_pages()

        table_id = parameters["tableId"]
        dataset_id = parameters['datasetId']
        project_id = parameters['projectId']

        categories: list[CategoriaCadastro] = PaginatorSlugCase(
            CategoriaListRequest(), CategoriasCadastro.poster,
            CategoriasCadastro.page_body_key).concat_all_pages()

        spread = list(map(spread_to_schema, resp))
        bigquery_rows = list(
            map(lambda r: set_categories(r, categories), spread))
        pprint(bigquery_rows[0])

        create_table_if_not_exists(client, table_id, dataset_id, project_id,
                                   schema.movimentos_schema,
                                   partition_field)
        insert_rows_bq(client, table_id, dataset_id, project_id,
                       bigquery_rows)

    except requests.exceptions.RequestException as e:
        return e
