"""
Dados (src/Staging): kpis.parquet, kpi_catalogo.csv e percentis.csv.
"""

import pandas as pd
import streamlit as st

from configuracao import PASTA_STAGING


@st.cache_data
def carregar_kpis():
    return pd.read_parquet(PASTA_STAGING / "kpis.parquet")


@st.cache_data
def carregar_catalogo():
    return pd.read_csv(PASTA_STAGING / "kpi_catalogo.csv").set_index("coluna")


@st.cache_data
def carregar_percentis():
    return pd.read_csv(PASTA_STAGING / "percentis.csv")


def linha_de_percentis(percentis, kpi, ano_num):
    filtro = (percentis["kpi"] == kpi) & (percentis["ano_num"] == ano_num)
    return percentis[filtro].iloc[0]


def valor_do_cenario(kpis, cenario, ano_num, kpi):
    filtro = (kpis["cenario"] == cenario) & (kpis["ano_num"] == ano_num)
    return kpis[filtro][kpi].iloc[0]
