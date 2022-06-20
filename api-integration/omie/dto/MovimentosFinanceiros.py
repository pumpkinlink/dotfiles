from dataclasses import dataclass, asdict, field
from typing import Literal, TypedDict, Callable, Any

import requests
from requests import Response

from dto.OmieEndpoint import OmieRequestBody, OmieResponseBodyCamelCase, \
    OmiePageRequestCamelCase
from utils.OmiePaginator import PaginatorCamelCase

URL = 'https://app.omie.com.br/api/v1/financas/mf/'


class Detalhes(TypedDict, total=False):
    """
    Detalhes do movimento financeiro.
    """
    nCodTitulo: int  # Código do titulo.+
    cCodIntTitulo: str  # Código de integração do título.+
    cNumTitulo: str  # Número do título.+
    dDtEmissao: str  # Data de emissão do título.
    dDtVenc: str  # Data de vencimento do título.
    dDtPrevisao: str  # Data de previsão de Pagamento/Recebimento.
    dDtPagamento: str  # Data de pagamento do título.
    nCodCliente: int  # Código de Cliente / Fornecedor.+
    cCPFCNPJCliente: str  # CPF/CNPJ do cliente.
    nCodCtr: int  # Código do contrato associado ao título.+
    cNumCtr: str  # Número do contrato associado ao título.+
    nCodOS: int  # Código do Pedido de Venda / Ordem de Serviço.+
    cNumOS: str  # Número do pedido de venda / Ordem de Serviço.+
    nCodCC: int  # Código da conta corrente.+
    cStatus: str  # Status do título.+
    cNatureza: str  # Natureza do título.+
    cTipo: str  # Tipo de documento.+
    cOperacao: str  # Operação do título.+
    cNumDocFiscal: str  # Número do documento fiscal (NF-e, NFC-e, NFS-e, etc)+
    cCodCateg: str  # Código da Categoria.
    cNumParcela: str  # Número da parcela "Formatada" como 999/999
    nValorTitulo: str  # Valor do título.
    nValorPIS: str  # Valor do PIS.
    cRetPIS: str  # Indica que o Valor do PIS informado deve ser retido.
    nValorCOFINS: str  # Valor do COFINS.
    cRetCOFINS: str  # Indica que o Valor do COFINS informado deve ser retido.
    nValorCSLL: str  # Valor do CSLL.
    cRetCSLL: str  # Indica que o Valor do CSLL informado deve ser retido.
    nValorIR: str  # Valor do Imposto de Renda.
    cRetIR: str  # Indica que o Valor do Imposto de Renda informado deve ser retido.
    nValorISS: str  # Valor do ISS.
    cRetISS: str  # Indica que o Valor do ISS informado deve ser retido.
    nValorINSS: str  # Valor do INSS.
    cRetINSS: str  # Indica que o Valor do INSS informado deve ser retido.
    cCodProjeto: int | None  # Código do projeto.+
    observacao: str  # Observações do título.
    cCodVendedor: int  # Código do vendedor.+
    nCodComprador: int  # Código do comprador.+
    cCodigoBarras: str  # Código de Barras do título.
    cNSU: str  # Número Sequencial Único - Comprovante de pagamento.
    nCodNF: int  # Código da Nota Fiscal.
    dDtRegistro: str  # Data de registro da NF.
    cNumBoleto: str  # Número do Boleto.
    cChaveNFe: str  # Chave da NF-e de origem.
    cOrigem: str  # Origem do lançamento.+
    nCodTitRepet: int  # Código do título original que gerou a repetição dos lançamentos.
    cGrupo: str  # Grupo do lançamento.
    nCodMovCC: int  # Código do movimento de Conta Corrente.
    nValorMovCC: str  # Valor do movimento de Conta Corrente.
    nCodMovCCRepet: int  # Código do movimento de repetição,
    nCodBaixa: int  # Código da baixa.
    dDtCredito: str  # Data de credito.
    dDtConcilia: str  # Data da conciliação.
    cHrConcilia: str  # string8	Hora de conciliação.
    cUsConcilia: str  # string10	Código do usuário responsável pela conciliação
    dDtInc: str  # Data de Inclusão.
    cHrInc: str  # Hora de Inclusão.
    cUsInc: str  # Usuário da Inclusão.
    dDtAlt: str  # Data de Alteração.
    cHrAlt: str  # Hora de Alteração.
    cUsAlt: str  # Usuário de alteração.


class Resumo(TypedDict, total=False):
    cLiquidado: str  # Indica se o título está liquidado.+
    nValPago: str  # Valor total pago para o título.
    nValAberto: str  # Valor total em aberto para o título.
    nDesconto: str  # Valor do Desconto.
    nJuros: str  # Valor do Juros.
    nMulta: str  # Valor da Multa.
    nValLiquido: str  # Valor líquido+


class Departamento(TypedDict, total=False):
    cCodDepartamento: str  # Código do Departamento.
    nDistrPercentual: str  # Percentual da distribuição.
    nDistrValor: str  # Valor da distribuição.
    nValorFixo: str  # Indica que o valor foi fixado na distribuição (S/N).


class Categoria(TypedDict, total=False):
    cCodCateg: str  # Código da Categoria.
    nDistrPercentual: str  # Percentual da distribuição.
    nDistrValor: str  # Valor da distribuição.
    nValorFixo: str  # Indica que o valor foi fixado na distribuição (S/N).


class Movimento(TypedDict, total=False):
    detalhes: Detalhes  # Detalhes do movimento financeiro.
    resumo: Resumo  # Situação do movimento financeiro.
    departamentos: list[Departamento] | None  # Distribuição por departamentos.
    categorias: list[Categoria] | None  # Distribuição por Categorias.


class MfListarResponse(OmieResponseBodyCamelCase, total=False):
    movimentos: list[
        Movimento]  # Listagem da movimentação financeira (Contas a Pagar, Contas a Receber e Lançamentos do Conta Corrente).


@dataclass(slots=True)
class MfListarRequest(OmiePageRequestCamelCase):
    """
    Solicitação de Listagem da movimentação financeira (Contas a Pagar, Contas a Receber e Lançamentos do Conta Corrente).
    """

    cOrdenarPor: Literal[
        'CODIGO', 'CODIGO_INTEGRACAO'] = None  # (string[100]):	Ordem de exibição dos dados.
    lDadosCad: bool = True  # Exibir dados cadastrais como a Data de Inclusão e Alteração do título (S/N)?
    dDtEmisDe: str = None  # (string[10]):	Data de emissão
    dDtEmisAte: str = None  # (string[10]):	Data de emissão
    dDtVencDe: str = None  # (string[10]):	Data de vencimento.
    dDtVencAte: str = None  # (string[10]):	Data de vencimento.
    dDtPagtoDe: str = '01/01/1901'  # (string[10]):	Data de pagamento
    dDtPagtoAte: str = None  # (string[10]):	Data de pagamento
    dDtPrevDe: str = None  # (string[10]):	Data de previsão de Pagamento/Recebimento.
    dDtPrevAte: str = None  # (string[10]):	Data de previsão de Pagamento/Recebimento.
    dDtRegDe: str = None  # (string[10]):	Data de registro da NF.
    dDtRegAte: str = None  # (string[10]):	Data de registro da NF.
    cNatureza: Literal[
        'P', 'R'] = None  # (string[1]):	Natureza do título.+
    dDtIncDe: str = None  # (string[10]):	Data de inclusão
    dDtIncAte: str = None  # (string[10]):	Data de inclusão
    dDtAltDe: str = None  # (string[10]):	Data de alteração
    dDtAltAte: str = None  # (string[10]):	Data de alteração
    cExibirDepartamentos: Literal[
        'S', 'N'] = 'S'  # Exibir distribuição por departamentos.
    cStatus: Literal[
        'CANCELADO',
        'RECEBIDO',
        'LIQUIDADO',
        'EMABERTO',
        'PAGTO_PARCIAL',
        'VENCEHOJE',
        'AVENCER',
        'ATRASADO'] = None  # string100	Status do título.+Pode ser:


@dataclass(slots=True)
class ListarMovimentosRequestBody(OmieRequestBody):
    param: list[MfListarRequest] = field(default_factory=list)
    call: str = "ListarMovimentos"


def listar_movimentos(params: MfListarRequest) -> Response:
    return requests.post(URL, json=asdict(
        ListarMovimentosRequestBody(param=[params])))


var1: ListarMovimentosRequestBody = ListarMovimentosRequestBody(
    param=[MfListarRequest(nPagina=1, dDtRegDe='01/01/2022')]
)


def get_paginator(object_hook: Callable[[dict], Any | None],
    request: MfListarRequest):
    return PaginatorCamelCase(
        request,
        poster=listar_movimentos,
        object_hook=object_hook,
        page_body_key="movimentos"
    )

# var2 : MfListarResponse = MfListarResponse(movimentos=[])
