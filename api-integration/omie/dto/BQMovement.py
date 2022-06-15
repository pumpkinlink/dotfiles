import datetime
import re

from dto import CategoriasCadastro, MovimentosFinanceiros, DepartamentosCadastro
from dto.ClientesCadastro import ClientesCadastroResumido
from dto.ContaCorrenteCadastro import ContaCorrente
from dto.ProjetosCadastro import Projeto

SOURCE_DATE_FORMAT = '%d/%m/%Y'
BIGQUERY_DATE_FORMAT = '%Y-%m-%d'


class BQCategory(MovimentosFinanceiros.Categoria):
    descricao_categoria: str | None


class BQDepartment(MovimentosFinanceiros.Categoria):
    descricao_departamento: str | None


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
    def compare_root_category(
        cc: CategoriasCadastro.CategoriaCadastro,
        code: str
    ):
        return cc['codigo'] == code

    mc = movement["detalhes"]["cCodCateg"]
    if mc is not None:
        result = next(
            filter(
                lambda cc: compare_root_category(cc=cc, code=mc),
                categories))
        return result['descricao'] if len(
            result) > 0 else None


def get_categories_array(
    movement: MovimentosFinanceiros.Movimento,
    categories: list[CategoriasCadastro.CategoriaCadastro]
) -> list[BQCategory]:
    def compare_array_category(
        cc: CategoriasCadastro.CategoriaCadastro,
        mc: MovimentosFinanceiros.Categoria
    ):
        return cc['codigo'] == mc['cCodCateg']

    def build_bq_cat(mc: MovimentosFinanceiros.Categoria) -> BQCategory:
        result = next(
            filter(lambda cc: compare_array_category(cc=cc, mc=mc), categories))
        desc = result['descricao'] if len(result) > 0 else None
        return {**mc, "descricao_categoria": desc}

    if 'categorias' not in movement:
        return []

    return list(map(build_bq_cat, movement["categorias"]))


def get_departments_array(
    movement: MovimentosFinanceiros.Movimento,
    departments: list[DepartamentosCadastro.Departamento]
) -> list[BQDepartment]:
    def build_bq_dep(md: MovimentosFinanceiros.Departamento) -> BQDepartment:
        result = next(
            filter(lambda dd: compare_array_department(dd=dd, md=md),
                   departments))
        desc = result['descricao'] if len(result) > 0 else None
        return {**md, 'descricao_departamento': desc}

    if 'departamentos' not in movement:
        return []

    return list(map(build_bq_dep, movement['departamentos']))


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


def build(
    m: MovimentosFinanceiros.Movimento,
    all_clients: list[ClientesCadastroResumido],
    all_categories: list[CategoriasCadastro.CategoriaCadastro],
    all_departments: list[DepartamentosCadastro.Departamento],
    all_checking_accounts: list[ContaCorrente],
    all_projects: list[Projeto]
):
    row: BQMovement = {
        **m['detalhes'],
        **m['resumo'],
        "razao_social_cliente": get_client_name(m, all_clients),
        "descricao_categoria": get_root_category(m, all_categories),
        "descricao_cc": get_account_name(m, all_checking_accounts),
        "nome_projeto": get_project_name(m, all_projects),
        "categorias": get_categories_array(m, all_categories),
        "departamentos": get_departments_array(m, all_departments),
    }
    return row


def compare_array_department(
    dd: DepartamentosCadastro.Departamento,
    md: MovimentosFinanceiros.Departamento
):
    return dd['codigo'] == md['cCodDepartamento']


def get_client_name(
    movement: MovimentosFinanceiros.Movimento,
    clients: list[ClientesCadastroResumido]
):
    code = movement["detalhes"]["nCodCliente"]

    def matches(client: ClientesCadastroResumido):
        return client['codigo_cliente'] == code

    result = next(filter(matches, clients))
    return result['razao_social']


def get_account_name(
    movement: MovimentosFinanceiros.Movimento,
    accounts: list[ContaCorrente]
):
    code = movement["detalhes"]['nCodCC']

    def matches(account: ContaCorrente):
        return account['nCodCC'] == code

    result = next(filter(matches, accounts))
    return result['descricao']


def get_project_name(
    movement: MovimentosFinanceiros.Movimento,
    projects: list[Projeto]
):
    if 'cCodProjeto' not in movement["detalhes"]:
        return None
    code = movement["detalhes"]['cCodProjeto']

    def matches(project: Projeto):
        return project['codigo'] == code

    result = next(filter(matches, projects))
    return result['nome']
