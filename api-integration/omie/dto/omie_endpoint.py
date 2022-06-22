import os
from dataclasses import dataclass
from typing import Sequence, TypedDict

app_key = os.environ.get("omie_app_key")
app_secret = os.environ.get("omie_app_secret")


@dataclass(slots=True)
class OmieRequestBody:
    call: str = None
    app_key: str = app_key
    app_secret: str = app_secret
    param: Sequence | None = None


class OmieResponseBodyCamelCase(TypedDict, total=True):
    nPagina: int  # Número da página que será listada.
    nTotPaginas: int  # Total de páginas encontradas.
    nRegistros: int  # Número de registros retornados
    nTotRegistros: int  # Total de registros encontrados.


class OmieResponseBodySlugCase(TypedDict, total=True):
    pagina: int  # Número da página que será listada.
    total_de_paginas: int  # Total de páginas encontradas.
    registros: int  # Número de registros retornados
    total_de_registros: int  # Total de registros encontrados.


@dataclass(slots=True)
class OmiePageRequestCamelCase:
    nPagina: int = 1  # Número da página que será listada.
    nRegPorPagina: int = 500  # Número de registros retornados (max 500)


@dataclass(slots=True)
class OmiePageRequestSlugCase:
    pagina: int = 1  # Número da página que será listada.
    registros_por_pagina: int = 500  # Número de registros retornados (max 500)
