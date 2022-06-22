import copy
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from typing import Any

from requests import Response

from dto.omie_endpoint import (
    OmieResponseBodyCamelCase,
    OmiePageRequestCamelCase,
    OmieResponseBodySlugCase,
    OmiePageRequestSlugCase,
)


def handle_error(response):
    if response.status_code != 200:
        logging.error(response.status_code, response.content)
        raise Exception(response.content)


def print_header(
    page_body_key: str,
    response: OmieResponseBodyCamelCase | OmieResponseBodySlugCase,
    page_number_key: str,
):
    header = {
        x: response[x] for x in response if x not in [page_body_key, page_number_key]
    }
    logging.info(f"{page_body_key} -> {header}")


@dataclass(slots=True)
class Paginator:
    page_body_key: str
    object_hook: Callable[[dict], Any | None]
    total_pages: int | None = None


class PaginatorSlugCase(Paginator):
    poster: Callable[[OmiePageRequestSlugCase], Response]
    request_params: OmiePageRequestSlugCase
    first_page: OmieResponseBodySlugCase = None

    def __init__(
        self,
        request_params: OmiePageRequestSlugCase,
        poster: Callable[..., Response],
        page_body_key: str,
        object_hook: Callable[[dict], Any | None] = None,
    ):
        self.poster = poster
        self.request_params = request_params
        self.object_hook = object_hook
        self.page_body_key = page_body_key

        self.request_params.pagina = 1
        try:
            response = self.post(request_params)
        except Exception as e:
            logging.error(e)
            raise e

        print_header(self.page_body_key, response, "pagina")

        self.first_page = response
        self.total_pages = self.first_page["total_de_paginas"]

    def post(self, request: OmiePageRequestSlugCase) -> OmieResponseBodySlugCase:
        response = self.poster(request)
        handle_error(response)

        response_body = json.loads(response.content, object_hook=self.object_hook)
        return response_body

    def get_page(self, page: int) -> OmieResponseBodySlugCase:
        logging.debug(
            f"{self.page_body_key} -> get page {page} {datetime.now().isoformat()}"
        )
        if page == 1 and self.first_page is not None:
            return self.first_page
        else:
            param = copy.deepcopy(self.request_params)
            param.pagina = page
            return self.post(param)

    def concat_all_pages(self) -> list:
        all_pages = map(self.get_page, range(1, self.total_pages + 1))

        all_page_bodies = map(lambda p: p[self.page_body_key], all_pages)
        return list(chain(*all_page_bodies))


class PaginatorCamelCase(Paginator):
    poster: Callable[[OmiePageRequestCamelCase], Response]
    request_params: OmiePageRequestCamelCase
    first_page: OmieResponseBodyCamelCase = None

    def __init__(
        self,
        request_params: OmiePageRequestCamelCase,
        poster: Callable[..., Response],
        object_hook: Callable[[dict], Any | None],
        page_body_key: str,
    ):
        self.poster = poster
        self.request_params = request_params
        self.object_hook = object_hook
        self.page_body_key = page_body_key

        self.request_params.nPagina = 1
        response = self.post(request_params)

        print_header(page_body_key, response, "nPagina")

        self.first_page = response
        self.total_pages = self.first_page["nTotPaginas"]

    def post(self, request: OmiePageRequestCamelCase) -> OmieResponseBodyCamelCase:
        response = self.poster(request)
        handle_error(response)

        response_body = json.loads(response.content, object_hook=self.object_hook)
        return response_body

    def get_page(self, page: int) -> OmieResponseBodyCamelCase:
        logging.debug(
            f"{self.page_body_key} -> get page {page} {datetime.now().isoformat()}"
        )
        if page == 1 and self.first_page is not None:
            return self.first_page
        else:
            param = copy.deepcopy(self.request_params)
            param.nPagina = page
            response = self.post(param)
            return response

    def concat_all_pages(self) -> list:
        all_pages = map(self.get_page, range(1, self.total_pages + 1))

        all_page_bodies = map(lambda p: p[self.page_body_key], all_pages)
        return list(chain(*all_page_bodies))