import datetime
import re

from dto import CategoriasCadastro, MovimentosFinanceiros, ClientesCadastro
from main import SOURCE_DATE_FORMAT, \
    BIGQUERY_DATE_FORMAT


class BQCategory(MovimentosFinanceiros.Categoria):
    descricao_categoria: str | None


class BQDepartment(MovimentosFinanceiros.Categoria):
    descricao_departamento: str


class BQMovement(
    MovimentosFinanceiros.Detalhes,
    MovimentosFinanceiros.Resumo
):
    razao_social_cliente: str
    descricao_cc: str
    nome_projeto: str
    descricao_categoria: str | None
    departamentos: list[BQDepartment]
    categorias: list[BQCategory]


partition_field = "dDtPagamento"


def get_root_category(
    movement: MovimentosFinanceiros.Movimento,
    categories: list[CategoriasCadastro.CategoriaCadastro]
):
    mc = movement["detalhes"]["cCodCateg"]
    if mc is not None:
        result = next(
            filter(
                lambda cc: compare_category(cc=cc, code=mc),
                categories))
        return result['descricao'] if len(
            result) > 0 else None


def get_categories_array(
    movement: MovimentosFinanceiros.Movimento,
    categories: list[CategoriasCadastro.CategoriaCadastro]
) -> list[BQCategory]:
    def build_bq_cat(mc: MovimentosFinanceiros.Categoria) -> BQCategory:
        result = next(
            filter(lambda cc: compare_array_category(cc=cc, mc=mc), categories))
        desc = result['descricao'] if len(result) > 0 else None
        return {**mc, "descricao_categoria": desc}

    return list(map(build_bq_cat, movement["categorias"]))

# def compare_department(
#     dd: DepartamentoCadastro.departamento,
#     md: MovimentosFinanceiros.Departamento
# ):
#     return dd['codigo'] == md['cCodDepartamento']

def bigquery_formatter(dct):
    for k, v in dct.items():
        if isinstance(v, str) and re.search("^dDt", k):
            dct[k] = datetime.datetime.strptime(v,
                                                SOURCE_DATE_FORMAT).date().strftime(
                BIGQUERY_DATE_FORMAT)
        elif isinstance(v, float) and k in [
            'nValorTitulo',
            'nValorPIS',
            'nValorCOFINS',
            'nValorCSLL',
            'nValorIR',
            'nValorISS',
            'nValorINSS',
            'nValorMovCC',

            'nValPago',
            'nValAberto',
            'nDesconto',
            'nJuros',
            'nMulta',
            'nValLiquido',

            'nDistrPercentual',
            'nDistrValor'
        ]:
            # Converte float para str, para que o Bigquery possa receber
            # os valores das colunas DECIMAL/NUMERIC sem perda de precisão
            dct[k] = str(v)
    return dct


def builder(
    m: MovimentosFinanceiros.Movimento,
    all_clients: list[ClientesCadastro.ClientesCadastroResumido],
    all_categories: list[CategoriasCadastro.CategoriaCadastro],
    # all_departments: list[DepartamentoCadastro.DepartamentoCadastro]
):
    row: BQMovement = {
        **m['detalhes'],
        **m['resumo'],
        "razao_social_cliente": get_client_name(m, all_clients),
        "descricao_categoria": get_root_category(m, all_categories),
        "categorias": get_categories_array(m, all_categories),
        # "departamentos": get_departments_array(m, all_departments),
        "departamentos": None,  # TODO
        "descricao_cc": None,
        "nome_projeto": None,

    }
    return row


def compare_array_category(
    cc: CategoriasCadastro.CategoriaCadastro,
    mc: MovimentosFinanceiros.Categoria
):
    return cc['codigo'] == mc['cCodCateg']


def compare_category(
    cc: CategoriasCadastro.CategoriaCadastro,
    code: str
):
    return cc['codigo'] == code


def get_client_name(
    movement: MovimentosFinanceiros.Movimento,
    clients: list[ClientesCadastro.ClientesCadastroResumido]
):
    code = movement["detalhes"]["nCodCliente"]

    def predicate(client: ClientesCadastro.ClientesCadastroResumido):
        return client['codigo_cliente'] == code

    result = next(filter(predicate, clients))
    return result['razao_social']
