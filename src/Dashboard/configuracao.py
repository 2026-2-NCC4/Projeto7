"""
Constantes do dashboard: pastas, perspectivas, unidades, cores e eventos de risco.
"""

from pathlib import Path

PASTA_STAGING = Path(__file__).resolve().parent.parent / "Staging"
ANO_BASE = 2026
OPCAO_MEDIANA = "Mediana dos 1.200 cenários"
PERSPECTIVAS = {
    "Gestão": {
        "pergunta": "Como estão a operação e o caixa?",
        "kpis": [
            "receita_liquida",
            "ebitda",
            "margem_ebitda",
            "dfc_fco",
            "saldo_final_caixa",
            "dfc_variacao_liquida",
        ],
        "kpi_padrao": "saldo_final_caixa",
        "colunas": 3,
    },
    "Investidores": {
        "pergunta": "O negócio gera retorno e distribui dividendos com folga?",
        "kpis": [
            "lucro_liquido",
            "eva",
            "fcl",
            "dfc_dividendos",
            "payout_caixa",
            "cobertura_dividendos",
        ],
        "kpi_padrao": "cobertura_dividendos",
        "colunas": 3,
    },
    "Controle": {
        "pergunta": "O lucro vira caixa? Como estão a cobertura de juros e os prazos?",
        "kpis": [
            "taxa_conversao",
            "fco_ebitda",
            "fco_lucro_liquido",
            "cobertura_juros_caixa",
            "pmr",
            "pmp",
            "ciclo_financeiro",
        ],
        "kpi_padrao": "fco_lucro_liquido",
        "colunas": 4,
    },
}
COR_DO_DELTA = {"maior é melhor": "normal", "menor é melhor": "inverse", "neutro": "off"}
CASAS_DECIMAIS = {"R$": 0, "%": 1, "dias": 1, "x": 2}
TITULO_DO_EIXO = {"R$": "R$ milhões", "%": "%", "dias": "dias", "x": "vezes (x)"}
COR_DA_FAIXA = "rgba(31, 119, 180, 0.20)"
COR_DA_MEDIANA = "#1f77b4"
COR_DO_CENARIO = "#d62728"
LIMITE_CAIXA_ZERADO = 1e6
EVENTOS_ADVERSOS = [
    "Caixa zerado (até R$ 1 mi)",
    "Caixa cai no ano",
    "Payout acima de 100%",
    "Cobertura de dividendos abaixo de 1",
]
COR_DOS_EVENTOS = {
    "Caixa zerado (até R$ 1 mi)": "#d62728",
    "Caixa cai no ano": "#ff7f0e",
    "Payout acima de 100%": "#2ca02c",
    "Cobertura de dividendos abaixo de 1": "#9467bd",
}
ANO_ENCERRAMENTO = 12
KPIS_DO_ANO_12 = [
    "dfc_caixa_inicial",
    "dfc_fco",
    "dfc_investimentos",
    "dfc_dividendos",
    "dfc_caixa_final",
]
ITENS_DA_PONTE = [
    "dfc_caixa_inicial",
    "dfc_fco",
    "dfc_investimentos",
    "dfc_juros_liquidos",
    "dfc_dividendos",
    "dfc_caixa_final",
]
COR_DE_AUMENTO = "#2ca02c"
COR_DE_QUEDA = "#d62728"
COR_DO_TOTAL = "#1f77b4"
WACC_BASE = 0.10
ALIQUOTA_BASE = 0.34
COR_DO_ESCOLHIDO = "#ff7f0e"
PENALIDADE_POR_ANO_DE_RISCO = 0.02
METRICAS_DO_SCORE = [
    {
        "nome": "VP dos EVAs",
        "peso": 0.25,
        "melhor": "Maior",
        "definicao": (
            "Valor criado acima do custo de capital: soma do EVA de cada ano, descontado ao WACC "
            "(2027 a 2038)."
        ),
    },
    {
        "nome": "EVA acumulado",
        "peso": 0.15,
        "melhor": "Maior",
        "definicao": (
            "Soma do EVA dos 12 anos, sem desconto. EVA = EBIT x (1 - alíquota) - capital "
            "investido x WACC."
        ),
    },
    {
        "nome": "Margem EBITDA média",
        "peso": 0.125,
        "melhor": "Maior",
        "definicao": (
            "EBITDA sobre a receita líquida, média dos 12 anos (inclui o Ano 12, de margem acima "
            "de 100%): quanto da receita vira geração operacional."
        ),
    },
    {
        "nome": "Lucro líquido acumulado",
        "peso": 0.125,
        "melhor": "Maior",
        "definicao": (
            "Soma do resultado final para o acionista nos 12 anos, depois de juros e impostos."
        ),
    },
    {
        "nome": "Liquidez corrente média",
        "peso": 0.10,
        "melhor": "Maior",
        "definicao": (
            "Ativo circulante sobre passivo circulante, média só dos anos em que o passivo "
            "circulante é positivo. Acima de 1, o curto prazo está coberto."
        ),
    },
    {
        "nome": "Caixa mínimo",
        "peso": 0.10,
        "melhor": "Maior",
        "definicao": (
            "Menor saldo final de caixa entre os 12 anos: o colchão de liquidez no pior momento."
        ),
    },
    {
        "nome": "PCT média",
        "peso": 0.075,
        "melhor": "Menor",
        "definicao": (
            "Participação de capital de terceiros: (passivo circulante + não circulante) sobre o "
            "patrimônio líquido, média só dos anos em que o passivo circulante e o patrimônio "
            "líquido são positivos."
        ),
    },
    {
        "nome": "Composição do endividamento média",
        "peso": 0.075,
        "melhor": "Menor",
        "definicao": (
            "Parcela da dívida que vence em até 12 meses: passivo circulante sobre (circulante + "
            "não circulante), média só dos anos em que o passivo circulante é positivo. No Ano 12 "
            "a base não informa passivo não circulante, então a CE desse ano é 100%."
        ),
    },
]
