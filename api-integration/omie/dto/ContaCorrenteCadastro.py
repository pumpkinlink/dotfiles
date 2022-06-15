from dataclasses import dataclass, field, asdict
from typing import Literal, TypedDict

import requests
from requests import Response

from dto.OmieEndpoint import OmieRequestBody, OmiePageRequestSlugCase, \
    OmieResponseBodySlugCase
from utils.OmiePaginator import PaginatorSlugCase

URL = 'https://app.omie.com.br/api/v1/geral/contacorrente/'


@dataclass
class FinContaCorrenteListarRequest(OmiePageRequestSlugCase):
    codigo: int = None  # Código da conta corrente no Omie.
    ordenar_por: Literal[
        'CODIGO', 'DATA_LANCAMENTO'] = None  # string100	Ordenar o resultado da página por
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


class ContaCorrente(TypedDict, total=False):
    nCodCC: int  # Código da conta corrente no Omie.
    descricao: str  # string40	Descrição da conta corrente.


class FinContaCorrenteResumoResponse(OmieResponseBodySlugCase):
    conta_corrente_lista: list[
        ContaCorrente]  # conta_corrente_listaArray	Lista de contas correntes


def listar_contas_correntes(params: FinContaCorrenteListarRequest) -> Response:
    return requests.post(URL, json=asdict(
        ListarContaCorrenteRequestBody(param=[params])))


def get_all() -> list[ContaCorrente]:
    return PaginatorSlugCase(
        FinContaCorrenteListarRequest(),
        poster=listar_contas_correntes,
        page_body_key='conta_corrente_lista'
    ).concat_all_pages()
