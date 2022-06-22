from dataclasses import dataclass, field, asdict
from typing import Literal, TypedDict

import requests
from requests import Response

from dto.omie_endpoint import (
    OmieRequestBody,
    OmiePageRequestSlugCase,
    OmieResponseBodySlugCase,
)
from utils.omie_paginator import PaginatorSlugCase

URL = "https://app.omie.com.br/api/v1/geral/projetos/"


@dataclass(slots=True)
class ProjListarRequest(OmiePageRequestSlugCase):
    ordenar_por: str = None  # string100	Ordenar o resultado da página por

    filtrar_apenas_inclusao: Literal[
        "S", "N"
    ] = None  # string1	Filtrar apenas registros incluídos (S/N)
    filtrar_apenas_alteracao: Literal[
        "S", "N"
    ] = None  # string1	Filtrar apenas registros alterados (S/N)

    ordem_descrescente: str = None  # string1	Indica se a ordem de exibição é decrescente caso seja informado "S".


@dataclass(slots=True)
class ProjListarRequestBody(OmieRequestBody):
    param: list[ProjListarRequest] = field(default_factory=list)
    call: str = "ListarProjetos"


class Projeto(TypedDict, total=False):
    codigo: int  # Código do projeto.
    nome: str  # string70	Nome do projeto.


class ProjListarResponse(OmieResponseBodySlugCase):
    cadastro: list[Projeto]


def listar_contas_correntes(params: ProjListarRequest) -> Response:
    return requests.post(URL, json=asdict(ProjListarRequestBody(param=[params])))


def get_all() -> list[Projeto]:
    return PaginatorSlugCase(
        ProjListarRequest(), poster=listar_contas_correntes, page_body_key="cadastro"
    ).concat_all_pages()
