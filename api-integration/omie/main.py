import datetime
import json
import re
from decimal_columns import Decimal
from http import HTTPStatus
from pprint import pprint

import functions_framework
import requests
from flask import Request, Response
from google.cloud import bigquery
from google.cloud.bigquery.enums import SqlTypeNames

from pandas import DataFrame

from dto import MovimentosFinanceiros
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse

SOURCE_DATE_FORMAT = '%d/%m/%Y'
BIGQUERY_DATE_FORMAT = '%Y-%m-%d'


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and re.search("^dDt", k):
            dct[k] = datetime.datetime.strptime(v,
                                                SOURCE_DATE_FORMAT).date().strftime(
                BIGQUERY_DATE_FORMAT)
        elif isinstance(v, str) and re.search("^nValorFixo$", k):
            dct[k] = (v == "S")
        elif isinstance(v, float) and k in [
            'nValorTitulo',
            'nValorPIS',
            'nValorCOFINS',
            'nValorCSLL',
            'nValorIR',
            'nValorISS',
            'nValorINSS',
            'nValorMovCC',
            'nDesconto',
            'nJuros',
            'nMulta',

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


REPEATED = 'REPEATED'
string = SqlTypeNames.STRING
integer = SqlTypeNames.INTEGER
numeric = SqlTypeNames.NUMERIC
field = bigquery.SchemaField
resumo = bigquery.SchemaField(name="resumo", field_type=SqlTypeNames.RECORD,
                              fields=(
                                            (
                                             field('cLiquidado',
                                             field('nValPago',
                                             field('nValAberto',
                                             field('nDesconto',
                                             field('nJuros',
                                             field('nMulta',
                                             field('nValLiquido')




                                            ))))
detalhes = bigquery.SchemaField(field_type=SqlTypeNames.RECORD, name="detalhes",
                                fields=(
                                    field('nCodTitulo', integer),
                                    field('cCodIntTitulo', string),
                                    field('cNumTitulo', string),
                                    field('dDtEmissao', string),
                                    field('dDtVenc', string),
                                    field('dDtPrevisao', string),
                                    field('dDtPagamento', string),
                                    field('nCodCliente', integer),
                                    field('cCPFCNPJCliente', string),
                                    field('nCodCtr', integer),
                                    field('cNumCtr', string),
                                    field('nCodOS', integer),
                                    field('cNumOS', string),
                                    field('nCodCC', integer),
                                    field('cStatus', string),
                                    field('cNatureza', string),
                                    field('cTipo', string),
                                    field('cOperacao', string),
                                    field('cNumDocFiscal', string),
                                    field('cCodCateg', string),
                                    field('cNumParcela', string),
                                    field('nValorTitulo', numeric),
                                    field('nValorPIS', numeric),
                                    field('cRetPIS', string),
                                    field('nValorCOFINS', numeric),
                                    field('cRetCOFINS', string),
                                    field('nValorCSLL', numeric),
                                    field('cRetCSLL', string),
                                    field('nValorIR', numeric),
                                    field('cRetIR', string),
                                    field('nValorISS', numeric),
                                    field('cRetISS', string),
                                    field('nValorINSS', numeric),
                                    field('cRetINSS', string),
                                    field('cCodProjeto', integer),
                                    field('observacao', string),
                                    field('cCodVendedor', integer),
                                    field('nCodComprador', integer),
                                    field('cCodigoBarras', string),
                                    field('cNSU', string),
                                    field('nCodNF', integer),
                                    field('dDtRegistro', string),
                                    field('cNumBoleto', string),
                                    field('cChaveNFe', string),
                                    field('cOrigem', string),
                                    field('nCodTitRepet', integer),
                                    field('cGrupo', string),
                                    field('nCodMovCC', integer),
                                    field('nValorMovCC', numeric),
                                    field('nCodMovCCRepet', integer),
                                    field('nDesconto', numeric),
                                    field('nJuros', numeric),
                                    field('nMulta', numeric),
                                    field('nCodBaixa', integer),
                                    field('dDtCredito', string),
                                    field('dDtConcilia', string),
                                    field('cHrConcilia', string),
                                    field('cUsConcilia', string),
                                    field('dDtInc', string),
                                    field('cHrInc', string),
                                    field('cUsInc', string),
                                    field('dDtAlt', string),
                                    field('cHrAlt', string),
                                    field('cUsAlt', string)
                                ))
boolean = SqlTypeNames.BOOLEAN
departamentos = bigquery.SchemaField(name="departamentos",
                                     field_type=SqlTypeNames.RECORD,
                                     mode=REPEATED,
                                     fields=(
                                         field('cCodDepartamento', string),
                                         field('nDistrPercentual', numeric),
                                         field('nDistrValor', numeric),
                                         field('nValorFixo', numeric)
                                     ))

categorias = field(name="categorias",
                   field_type=SqlTypeNames.RECORD,
                   mode=REPEATED, fields=(
        field('cCodCateg', string),
        field('nDistrPercentual', numeric),
        field('nDistrValor', numeric),
        field('nValorFixo', boolean)
    ))
movimentos_schema = [
    detalhes,
    resumo,
    departamentos,
    categorias
]


@functions_framework.http
def hello(request: Request):
    parameters = request.get_json(silent=True)
    try:
        resp = MovimentosFinanceiros.listar_movimentos(
            MfListarRequest(nRegPorPagina=1, dDtRegDe='01/01/2022'))

        if 200 <= resp.status_code < 300:
            response_body: MfListarResponse = json.loads(resp.content,
                                                         object_hook=datetime_parser)
            pprint(response_body)
            dataframe = DataFrame.from_records(response_body['movimentos'])

            return response_body['nRegistros']
        else:
            return resp.status_code

    except requests.exceptions.RequestException as e:
        return Response(e, HTTPStatus.INTERNAL_SERVER_ERROR)


hello(None)
