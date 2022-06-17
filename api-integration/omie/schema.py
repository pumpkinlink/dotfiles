from google.cloud.bigquery import SqlTypeNames, SchemaField

REPEATED = 'REPEATED'
STRING = SqlTypeNames.STRING
INTEGER = SqlTypeNames.INTEGER
NUMERIC = SqlTypeNames.NUMERIC
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
movimentos_schema: list[SchemaField] = [
    *detalhes,
    *resumo,
    departamentos,
    categorias,
]
