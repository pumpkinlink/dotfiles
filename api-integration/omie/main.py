import datetime
import json
import re
from decimal import Decimal
from pprint import pprint

import functions_framework
import requests

from pandas import DataFrame

from dto import MovimentosFinanceiros
from dto.MovimentosFinanceiros import MfListarRequest, MfListarResponse

DATE_FORMAT = '%d/%m/%Y'


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and re.search("^dDt", k):
            dct[k] = datetime.datetime.strptime(v, DATE_FORMAT).date()
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
            dct[k] = Decimal(str(v))

    return dct


@functions_framework.http
def hello(request):
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
        return e


hello(None)
