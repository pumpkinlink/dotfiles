from dataclasses import dataclass, field, asdict
from typing import TypedDict, Literal

import requests
from requests import Response

from dto.OmieEndpoint import OmieRequestBody, OmiePageRequestSlugCase, \
    OmieResponseBodySlugCase
from utils.OmiePaginator import PaginatorSlugCase

URL = 'https://app.omie.com.br/api/v1/geral/categorias/'


@dataclass(slots=True)
class CategoriaListRequest(OmiePageRequestSlugCase):
    filtrar_apenas_ativo: Literal[
        'S', 'N'] = "N"  # Fitrar apenas categorias ativas


@dataclass(slots=True)
class ListarCategoriasRequestBody(OmieRequestBody):
    param: list[CategoriaListRequest] = field(default_factory=list)
    call: str = "ListarCategorias"


class CategoriaCadastro(TypedDict, total=False):
    codigo: str  # string20	 Código para a Categoria
    descricao: str  # string50	 Descrição para a Categoria
    codigo_dre: str  # string10	Código no DRE


class CategoriaListFullResponse(OmieResponseBodySlugCase, total=False):
    categoria_cadastro: list[CategoriaCadastro]


def listar_categorias(params: CategoriaListRequest) -> Response:
    return requests.post(URL, json=asdict(
        ListarCategoriasRequestBody(param=[params])))


def get_all() -> list[CategoriaCadastro]:
    return PaginatorSlugCase(
        CategoriaListRequest(),
        poster=listar_categorias,
        page_body_key='categoria_cadastro'
    ).concat_all_pages()
