from dataclasses import dataclass, field, asdict
from typing import Literal, TypedDict

import requests

from dto.OmieEndpoint import OmieRequestBody, OmiePageRequestSlugCase, \
    OmieResponseBodySlugCase

URL = 'https://app.omie.com.br/api/v1/geral/contacorrente/'


@dataclass
class FinContaCorrenteListarRequest(OmiePageRequestSlugCase):
    codigo: int = None  # Código da conta corrente no Omie.
    ordenar_por: Literal[
        'CODIGO', 'DATA_LANCAMENTO'] = None  # string100	Ordenar o resultado da página por

    # noinspection SpellCheckingInspection
    ordem_descrescente: str = None  # string1	Indica se a ordem de exibição é decrescente caso seja informado "S".
    # ####### (Sim, ta escrito errado mesmo)

    filtrar_por_data_de: str = None  # string10	Filtrar lançamentos incluídos e/ou alterados até a data
    filtrar_por_data_ate: str = None  # string10	Filtrar lançamentos incluídos e/ou alterados até a data
    filtrar_apenas_inclusao: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas registros incluídos (S/N)
    filtrar_apenas_alteracao: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas registros alterados (S/N)
    filtrar_apenas_ativo: Literal[
        'S', 'N'] = None  # string1	Filtrar apenas contas correntes ativas


@dataclass
class ListarContaCorrenteRequestBody(OmieRequestBody):
    param: list[FinContaCorrenteListarRequest] = field(default_factory=list)
    call: str = "ListarResumoContasCorrentes"


class ContaCorrenteLista(TypedDict, total=False):
    nCodCC: int  # Código da conta corrente no Omie.
    cCodCCInt: str  # string20	Código de Integração do Parceiro.
    descricao: str  # string40	Descrição da conta corrente.
    codigo_banco: str  # string3	Código do banco.+
    codigo_agencia: str  # string10	Código da Agência
    conta_corrente: str  # string15	Número da conta corrente.
    nome_gerente: str  # string40	Nome do Gerente da Conta Corrente.
    tipo: str  # string2	Tipo da Conta Corrente.+
    tipo_comunicacao: str  # text	Tipo de comunicação
    cSincrAnalitica: str  # string1	Sincroniza os Movimentos de Forma Análitica para o PDV
    nTpTef: int  # Tipo de TEF
    nTaxaAdm: str  # decimal	Taxa da Administradora de Cartões
    nDiasVenc: int  # Dias para vencimento
    nNumParc: int  # Número máximo de parcelas do Cartão de Credito
    nCodAdm: int  # Código da Administradora de Cartões
    cUtilPDV: str  # string1	Utiliza a Conta Corrente no OmiePDV
    cCategoria: str  # string20	Código da Categoria para o PDV.
    cModalidade: str  # string3	Modalidade da Cobrança
    saldo_inicial: str  # decimal	Saldo Inicial da Conta Corrente
    saldo_data: str  # string10	Data do Saldo Inicial da Conta Corrente
    valor_limite: str  # decimal	Valor do Limite do Crédito
    cTipoCartao: str  # string1	Tipo de Cartão para Administradoras de Cartão.+


class FinContaCorrenteResumoResponse(OmieResponseBodySlugCase):
    conta_corrente_lista: list[
        ContaCorrenteLista]  # conta_corrente_listaArray	Lista de contas correntes


page_body_key = 'conta_corrente_lista'


def listar_categorias(params: FinContaCorrenteListarRequest):
    return requests.post(URL, json=asdict(
        ListarContaCorrenteRequestBody(param=[params])))


poster = listar_categorias
