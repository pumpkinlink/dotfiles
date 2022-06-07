from dataclasses import dataclass, field, asdict
from typing import TypedDict

import requests

from dto.OmieRequestBody import OmieRequestBody

URL = 'https://app.omie.com.br/api/v1/geral/clientes/'


class ClientesCadastroResumido(TypedDict, total=False):
    codigo_cliente: int  # Código de Cliente / Fornecedor
    codigo_cliente_integracao: str  # string20	Código de Integração com sistemas legados.
    razao_social: str  # string60	Razão Social+
    nome_fantasia: str  # string100	Nome Fantasia+
    cnpj_cpf: str  # string20	CNPJ / CPF+


class ClientesListResponse(TypedDict, total=False):
    pagina: int  # Número da página retornada
    total_de_paginas: int  # Número total de páginas
    registros: int  # Número de registros retornados na página.
    total_de_registros: int  # total de registros encontrados
    clientes_cadastro_resumido: list[
        ClientesCadastroResumido]  # Cadastro reduzido de produtos


@dataclass
class ClientesPorCodigo:
    codigo_cliente_omie: int | None = None  # Código de Cliente / Fornecedor
    codigo_cliente_integracao: str | None = None  # string20	Código de Integração com sistemas legados.


@dataclass
class ClientesListRequest:
    apenas_importado_api: str | None = None  # string1	Exibir apenas os registros gerados pela API
    ordenar_por: str | None = None  # string100	Ordem de exibição dos dados. Padrão: Código.
    ordem_decrescente: str | None = None  # string1	Se a lista será apresentada em ordem decrescente.
    filtrar_por_data_de: str | None = None  # string10	Filtrar os registros a partir de uma data.
    filtrar_por_data_ate: str | None = None  # string10	Filtrar os registros até uma data.
    filtrar_por_hora_de: str | None = None  # string8	Filtro por hora a partir de.
    filtrar_por_hora_ate: str | None = None  # string8	Filtro por hora até.
    filtrar_apenas_inclusao: str | None = None  # string1	Filtrar apenas os registros incluídos.
    filtrar_apenas_alteracao: str | None = None  # string1	Filtrar apenas os registros alterados.
    # clientesFiltro:	clientesFiltro	Filtrar cadastro de clientes
    clientesPorCodigo: list[ClientesPorCodigo] = field(
        default_factory=list)  # Lista de Códigos para filtro de clientes
    exibir_caracteristicas: str | None = None  # string1	Exibe as caracteristicas do cliente.

    pagina: int = 1  # Número da página retornada
    registros_por_pagina: int = 500  # Número de registros retornados na página.


@dataclass
class ListarCategoriasRequestBody(OmieRequestBody):
    param: list[ClientesListRequest] = field(default_factory=list)
    call: str = "ListarClientesResumido"


def listar_categorias(params: ClientesListRequest):
    return requests.post(URL, json=asdict(
        ListarCategoriasRequestBody(param=[params])))
