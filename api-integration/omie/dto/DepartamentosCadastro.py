from dataclasses import dataclass, field, asdict
from typing import TypedDict, Literal

import requests
from requests import Response

from dto.OmieEndpoint import OmieRequestBody, OmiePageRequestSlugCase, \
    OmieResponseBodySlugCase
from utils.OmiePaginator import PaginatorSlugCase

URL = 'https://app.omie.com.br/api/v1/geral/departamentos/'


@dataclass
class DepartamentoListarRequest(OmiePageRequestSlugCase):
    pass


@dataclass
class ListarDepartamentosRequestBody(OmieRequestBody):
    param: list[DepartamentoListarRequest] = field(default_factory=list)
    call: str = "ListarDepartamentos"


class Departamento(TypedDict, total=False):
    codigo: str  # string40	Código do Departamento / Centro de Custo
    descricao: str  # string50	Nome do Departamento / Centro de Custo


class DepartamentoListarResponse(OmieResponseBodySlugCase, total=False):
    departamentos: list[Departamento]


def listar_departamentos(params: DepartamentoListarRequest) -> Response:
    return requests.post(URL, json=asdict(
        ListarDepartamentosRequestBody(param=[params])))


def get_all() -> list[Departamento]:
    return PaginatorSlugCase(
        DepartamentoListarRequest(),
        poster=listar_departamentos,
        page_body_key='departamentos'
    ).concat_all_pages()
