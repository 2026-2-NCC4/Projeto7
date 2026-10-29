"""
Dados (src/Staging): kpis.parquet, kpi_catalogo.csv e percentis.csv.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

PASTA_STAGING = Path(__file__).resolve().parent.parent / "Staging"
ANO_BASE = 2026
OPCAO_MEDIANA = "Mediana dos 1.200 cenários"
KPIS_PRINCIPAIS = [
    "receita_liquida",
    "ebitda",
    "margem_ebitda",
    "lucro_liquido",
    "saldo_final_caixa",
    "eva",
]
COR_DO_DELTA = {"maior é melhor": "normal", "menor é melhor": "inverse", "neutro": "off"}


@st.cache_data
def carregar_kpis():
    return pd.read_parquet(PASTA_STAGING / "kpis.parquet")


@st.cache_data
def carregar_catalogo():
    return pd.read_csv(PASTA_STAGING / "kpi_catalogo.csv").set_index("coluna")


@st.cache_data
def carregar_percentis():
    return pd.read_csv(PASTA_STAGING / "percentis.csv")


def numero_br(valor, casas):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar(valor, unidade):
    if pd.isna(valor):
        return "n/d"
    if unidade == "R$":
        return "R$ " + numero_br(valor / 1e6, 0) + " mi"
    if unidade == "%":
        return numero_br(valor * 100, 1) + "%"
    if unidade == "dias":
        return numero_br(valor, 1) + " dias"
    return numero_br(valor, 2) + "x"


def formatar_diferenca(diferenca, unidade):
    sinal = "+" if diferenca >= 0 else "-"
    absoluto = abs(diferenca)
    if unidade == "R$":
        return sinal + "R$ " + numero_br(absoluto / 1e6, 0) + " mi"
    if unidade == "%":
        return sinal + numero_br(absoluto * 100, 1) + " p.p."
    if unidade == "dias":
        return sinal + numero_br(absoluto, 1) + " dias"
    return sinal + numero_br(absoluto, 2) + "x"


def rotulo_ano(ano_num):
    texto = f"{ANO_BASE + ano_num} (Ano {ano_num})"
    if ano_num == 12:
        texto = texto + " - encerramento"
    return texto


def linha_de_percentis(percentis, kpi, ano_num):
    filtro = (percentis["kpi"] == kpi) & (percentis["ano_num"] == ano_num)
    return percentis[filtro].iloc[0]


def valor_do_cenario(kpis, cenario, ano_num, kpi):
    filtro = (kpis["cenario"] == cenario) & (kpis["ano_num"] == ano_num)
    return kpis[filtro][kpi].iloc[0]


def mostrar_cartao(coluna_da_tela, kpi, catalogo, percentis, kpis, cenario, ano_num):
    nome = catalogo.loc[kpi, "nome"]
    unidade = catalogo.loc[kpi, "unidade"]
    direcao = catalogo.loc[kpi, "direcao"]

    faixa = linha_de_percentis(percentis, kpi, ano_num)
    mediana = faixa["p50"]
    texto_faixa = formatar(faixa["p5"], unidade) + " a " + formatar(faixa["p95"], unidade)

    with coluna_da_tela:
        if cenario == OPCAO_MEDIANA:
            st.metric(nome, formatar(mediana, unidade))
            st.caption("Faixa de 90% dos cenários: " + texto_faixa)
        else:
            valor = valor_do_cenario(kpis, cenario, ano_num, kpi)
            diferenca = formatar_diferenca(valor - mediana, unidade) + " vs mediana"
            st.metric(nome, formatar(valor, unidade), delta=diferenca, delta_color=COR_DO_DELTA[direcao])
            texto = "Mediana: " + formatar(mediana, unidade) + " | faixa de 90%: " + texto_faixa
            if valor < faixa["p5"] or valor > faixa["p95"]:
                texto = texto + " | fora da faixa de 90%"
            st.caption(texto)


def main():
    st.set_page_config(page_title="Grafix - CTI", layout="wide")

    kpis = carregar_kpis()
    catalogo = carregar_catalogo()
    percentis = carregar_percentis()

    st.sidebar.header("Filtros")
    cenarios = [OPCAO_MEDIANA] + sorted(kpis["cenario"].unique())
    cenario = st.sidebar.selectbox("Cenário", cenarios)
    ano_num = st.sidebar.selectbox("Ano", list(range(1, 13)), index=4, format_func=rotulo_ano)

    st.title("Grafix - Plataforma Analítica de Planejamento Financeiro")
    st.write(
        "Concessionária de rodovias (case CTI Global): a base traz 1.200 futuros possíveis "
        "da mesma concessão, de 2027 (Ano 1) a 2038 (Ano 12, encerramento do contrato). "
        "Sem cenário escolhido, os cartões mostram a **mediana** dos 1.200 e a faixa em que "
        "ficam 90% deles (P5 a P95). Ao escolher um cenário na barra lateral, cada cartão "
        "compara o valor dele com a mediana."
    )

    if ano_num == 12:
        st.info(
            "O Ano 12 é o encerramento da concessão: margem EBITDA acima de 100% "
            "e contas ausentes são esperados nesse ano."
        )

    st.subheader(cenario + " - " + rotulo_ano(ano_num))

    colunas_da_tela = st.columns(3) + st.columns(3)
    for coluna_da_tela, kpi in zip(colunas_da_tela, KPIS_PRINCIPAIS):
        mostrar_cartao(coluna_da_tela, kpi, catalogo, percentis, kpis, cenario, ano_num)

    st.caption(
        "Fonte: CTI Global, projeção anonimizada (Ano 1 = 2027). A mediana é calculada por KPI "
        "e por ano e não corresponde a um cenário real. Valores em R$ milhões; margens em %."
    )


main()
