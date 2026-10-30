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
