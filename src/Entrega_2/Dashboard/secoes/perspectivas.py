"""
Seção das abas por perspectiva (Gestão, Investidores e Controle): cartões e gráfico da faixa P5 a P95.
"""

import plotly.graph_objects as go
import streamlit as st

from componentes import aplicar_estilo, mostrar_cartoes
from configuracao import (
    CASAS_DECIMAIS,
    COR_DA_FAIXA,
    COR_DA_MEDIANA,
    COR_DO_CENARIO,
    OPCAO_MEDIANA,
    PERSPECTIVAS,
    TITULO_DO_EIXO,
)
from formatacao import converter_para_exibicao


def montar_grafico_faixa(kpi, catalogo, percentis, kpis, cenario, ano_num):
    nome = catalogo.loc[kpi, "nome"]
    unidade = catalogo.loc[kpi, "unidade"]
    formato = "%{y:,." + str(CASAS_DECIMAIS[unidade]) + "f}"

    serie = percentis[percentis["kpi"] == kpi].sort_values("ano_num")
    anos = serie["ano_calendario"]

    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=anos,
            y=converter_para_exibicao(serie["p95"], unidade),
            mode="lines",
            line={"width": 0},
            showlegend=False,
            hovertemplate="P95: " + formato + "<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=anos,
            y=converter_para_exibicao(serie["p5"], unidade),
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor=COR_DA_FAIXA,
            name="Faixa de 90% (P5 a P95)",
            hovertemplate="P5: " + formato + "<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=anos,
            y=converter_para_exibicao(serie["p50"], unidade),
            mode="lines+markers",
            line={"color": COR_DA_MEDIANA},
            name="Mediana dos 1.200 cenários",
            hovertemplate="Mediana: " + formato + "<extra></extra>",
        )
    )
    if cenario != OPCAO_MEDIANA:
        linhas = kpis[kpis["cenario"] == cenario].sort_values("ano_num")
        figura.add_trace(
            go.Scatter(
                x=linhas["ano_calendario"],
                y=converter_para_exibicao(linhas[kpi], unidade),
                mode="lines+markers",
                line={"color": COR_DO_CENARIO},
                name=cenario,
                hovertemplate=cenario + ": " + formato + "<extra></extra>",
            )
        )

    eixo_y = {"title": TITULO_DO_EIXO[unidade], "automargin": True}
    aplicar_estilo(figura, nome + " por ano", 380, ano_num, eixo_y)
    return figura


def mostrar_perspectivas(catalogo, percentis, kpis, cenario, ano_num):
    nomes_das_abas = list(PERSPECTIVAS)
    abas = st.tabs(nomes_das_abas)
    for aba, nome_da_aba in zip(abas, nomes_das_abas):
        perspectiva = PERSPECTIVAS[nome_da_aba]
        with aba:
            st.markdown("**" + perspectiva["pergunta"] + "**")
            mostrar_cartoes(
                perspectiva["kpis"],
                perspectiva["colunas"],
                catalogo,
                percentis,
                kpis,
                cenario,
                ano_num,
            )

            nomes_dos_kpis = {kpi: catalogo.loc[kpi, "nome"] for kpi in perspectiva["kpis"]}
            kpi_do_grafico = st.selectbox(
                "Indicador no gráfico",
                perspectiva["kpis"],
                index=perspectiva["kpis"].index(perspectiva["kpi_padrao"]),
                format_func=nomes_dos_kpis.get,
                key="indicador_" + nome_da_aba,
            )
            figura = montar_grafico_faixa(kpi_do_grafico, catalogo, percentis, kpis, cenario, ano_num)
            st.plotly_chart(figura, key="grafico_" + nome_da_aba)
