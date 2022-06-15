from dataclasses import dataclass, field, asdict
from typing import TypedDict, Literal

import requests
from requests import Response

from dto.OmieEndpoint import OmieRequestBody, OmiePageRequestSlugCase, \
    OmieResponseBodySlugCase
from utils.OmiePaginator import PaginatorSlugCase

URL = 'https://app.omie.com.br/api/v1/geral/categorias/'


class DadosDre(TypedDict, total=False):
    codigoDRE: str  # string10	Código da Conta do DRE.
    descricaoDRE: str  # string40	Descrição da Conta do DRE.
    naoExibirDRE: str  # string1	Indica se a Conta está marcada para não exibir no DRE.
    nivelDRE: int  # Nível da Conta da DRE.
    sinalDRE: str  # string1	Sinal da Conta para o DRE.
    totalizaDRE: str  # string1	Indica se a Conta do DRE é Totalizadora.


class CategoriaCadastro(TypedDict, total=False):
    categoria_superior: str  # text	 Código da Categoria de Nivel Superior
    codigo: str  # string20	 Código para a Categoria
    descricao: str  # string50	 Descrição para a Categoria
    descricao_padrao: str  # string50	 Descrição Padrão para a Categoria
    conta_inativa: str  # string1	 Indica que a conta está inativo
    definida_pelo_usuario: str  # string1	 Indica que a conta financeira é definida pelo usuário
    id_conta_contabil: int  # ID da Conta Contábil
    tag_conta_contabil: str  # string20	 Tag para Conta Contábil
    conta_despesa: str  # string1	 Quando S, indica que é conta de despesa
    nao_exibir: str  # string1	 Indica que a Categoria não deve ser exibida em ComboBox
    natureza: str  # string10	 Descrição da Natureza da conta
    conta_receita: str  # string1	 Quando S, indica que é conta de receita
    totalizadora: str  # string1	 Quando S, indica que é totalizadora de conta
    transferencia: str  # string1	 Quando S, indica que é categoria de transferência
    codigo_dre: str  # string10	Código no DRE
    dadosDRE: DadosDre  # Detalhes da conta do DRE.


class categoria_listfull_response(OmieResponseBodySlugCase, total=False):
    categoria_cadastro: list[CategoriaCadastro]


@dataclass
class CategoriaListRequest(OmiePageRequestSlugCase):
    filtrar_apenas_ativo: Literal[
        'S', 'N'] = "N"  # Fitrar apenas categorias ativas


@dataclass
class ListarCategoriasRequestBody(OmieRequestBody):
    param: list[CategoriaListRequest] = field(default_factory=list)
    call: str = "ListarCategorias"


def listar_categorias(params: CategoriaListRequest) -> Response:
    return requests.post(URL, json=asdict(
        ListarCategoriasRequestBody(param=[params])))


def get() -> list[CategoriaCadastro]:
    return PaginatorSlugCase(
        CategoriaListRequest(),
        poster = listar_categorias,
        page_body_key = 'categoria_cadastro'
    ).concat_all_pages()
