from dataclasses import dataclass, field, asdict
from typing import Literal

import requests

from dto.OmieEndpoint import OmieRequestBody

URL = 'https://app.omie.com.br/api/v1/geral/contacorrente/'


@dataclass
class FinContaCorrenteListarRequest:
    pagina: int = 1  # Número da página retornada
    registros_por_pagina: int = 500  # Número de registros retornados na página.

    codigo: int = None  # Código da conta corrente no Omie.
    ordenar_por: Literal[
        'CODIGO', 'DATA_LANCAMENTO'] = None  # string100	Ordenar o resultado da página por

    # noinspection SpellCheckingInspection
    ordem_descrescente: str = None  # string1	Indica se a ordem de exibição é decrescente caso seja informado "S".
    # ####### (Sim, ta escrito errado mesmo)

    filtrar_por_data_de: str = None  # string10	Filtrar lançamentos incluídos e/ou alterados até a data
    filtrar_por_data_ate: str = None  # string10	Filtrar lançamentos incluídos e/ou alterados até a data
    filtrar_apenas_inclusao: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas registros incluídos (S/N)
    filtrar_apenas_alteracao: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas registros alterados (S/N)
    filtrar_apenas_ativo: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas contas correntes ativas


@dataclass
class ListarContaCorrenteRequestBody(OmieRequestBody):
    param: list[FinContaCorrenteListarRequest] = field(default_factory=list)
    call: str = "ListarResumoContasCorrentes"


def listar_categorias(params: FinContaCorrenteListarRequest):
    return requests.post(URL, json=asdict(
        ListarContaCorrenteRequestBody(param=[params])))
