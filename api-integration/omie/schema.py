import datetime
import re

from google.cloud.bigquery import SqlTypeNames, SchemaField

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


REPEATED = 'REPEATED'
STRING = SqlTypeNames.STRING
INTEGER = SqlTypeNames.INTEGER
NUMERIC = SqlTypeNames.NUMERIC
BOOLEAN = SqlTypeNames.BOOLEAN
DATE = SqlTypeNames.DATE
TIME = SqlTypeNames.TIME
field = SchemaField
resumo = [
    field('cLiquidado', STRING),
    field('nValPago', NUMERIC),
    field('nValAberto', NUMERIC),
    field('nDesconto', NUMERIC),
    field('nJuros', NUMERIC),
    field('nMulta', NUMERIC),
    field('nValLiquido', NUMERIC)
]
detalhes = [
    field('nCodTitulo', INTEGER),
    field('cCodIntTitulo', STRING),
    field('cNumTitulo', STRING),

    field('dDtEmissao', DATE),
    field('dDtVenc', DATE),
    field('dDtPrevisao', DATE),
    field('dDtPagamento', DATE),

    field('nCodCliente', INTEGER),
    field('cCPFCNPJCliente', STRING),
    field('razao_social_cliente', STRING),
    # cliente

    field('nCodCtr', INTEGER),
    field('cNumCtr', STRING),
    field('nCodOS', INTEGER),
    field('cNumOS', STRING),

    field('nCodCC', INTEGER),
    field('descricao_cc', STRING),
    # conta corrente

    field('cStatus', STRING),
    field('cNatureza', STRING),
    field('cTipo', STRING),
    field('cOperacao', STRING),
    field('cNumDocFiscal', STRING),
    field('cCodCateg', STRING),
    field('descricao_categoria', STRING),
    field('cNumParcela', STRING),

    field('nValorTitulo', NUMERIC),
    field('nValorPIS', NUMERIC),
    field('cRetPIS', STRING),
    field('nValorCOFINS', NUMERIC),
    field('cRetCOFINS', STRING),
    field('nValorCSLL', NUMERIC),
    field('cRetCSLL', STRING),
    field('nValorIR', NUMERIC),
    field('cRetIR', STRING),
    field('nValorISS', NUMERIC),
    field('cRetISS', STRING),
    field('nValorINSS', NUMERIC),
    field('cRetINSS', STRING),

    field('cCodProjeto', INTEGER),
    field('nome_projeto', STRING),
    # projeto

    field('observacao', STRING),

    field('cCodVendedor', INTEGER),
    field('nCodComprador', INTEGER),

    field('cCodigoBarras', STRING),
    field('cNSU', STRING),
    field('nCodNF', INTEGER),
    field('dDtRegistro', DATE),
    field('cNumBoleto', STRING),
    field('cChaveNFe', STRING),
    field('cOrigem', STRING),
    field('nCodTitRepet', INTEGER),
    field('cGrupo', STRING),
    field('nCodMovCC', INTEGER),
    field('nValorMovCC', NUMERIC),
    field('nCodMovCCRepet', INTEGER),
    field('nCodBaixa', INTEGER),
    field('dDtCredito', DATE),

    field('dDtConcilia', DATE),
    field('cHrConcilia', TIME),
    field('cUsConcilia', STRING),

    field('dDtInc', DATE),
    field('cHrInc', TIME),
    field('cUsInc', STRING),

    field('dDtAlt', DATE),
    field('cHrAlt', TIME),
    field('cUsAlt', STRING)
]
departamentos = field(name="departamentos",
                      field_type=SqlTypeNames.RECORD,
                      mode=REPEATED,
                      fields=(
                          field('cCodDepartamento', STRING),
                          field('descricao_departamento', STRING),
                          field('nDistrPercentual', NUMERIC),
                          field('nDistrValor', NUMERIC),
                          field('nValorFixo', STRING)
                      ))
categorias = field(name="categorias",
                   field_type=SqlTypeNames.RECORD,
                   mode=REPEATED,
                   fields=(
                       field('cCodCateg', STRING),
                       field('descricao_categoria', STRING),
                       field('nDistrPercentual', NUMERIC),
                       field('nDistrValor', NUMERIC),
                       field('nValorFixo', STRING)
                   ))
partition_field = "dDtPagamento"
movimentos_schema = [
    *detalhes,
    *resumo,
    departamentos,
    categorias,
]


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
