"""
Seção "Risco ao longo dos anos": em quantos cenários cada evento adverso acontece, ano a ano.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from componentes import aplicar_estilo
from configuracao import COR_DOS_EVENTOS, EVENTOS_ADVERSOS, LIMITE_CAIXA_ZERADO
from formatacao import numero_br


def marcar_eventos(kpis):
    return pd.DataFrame(
        {
            "ano_num": kpis["ano_num"],
            "ano_calendario": kpis["ano_calendario"],
            EVENTOS_ADVERSOS[0]: kpis["saldo_final_caixa"] <= LIMITE_CAIXA_ZERADO,
            EVENTOS_ADVERSOS[1]: kpis["dfc_variacao_liquida"] < 0,
            EVENTOS_ADVERSOS[2]: kpis["payout_caixa"] > 1,
            EVENTOS_ADVERSOS[3]: kpis["cobertura_dividendos"] < 1,
        }
    )


def calcular_risco_por_ano(kpis):
    eventos = marcar_eventos(kpis)
    por_ano = eventos.groupby(["ano_num", "ano_calendario"])[EVENTOS_ADVERSOS]
    contagem = por_ano.sum().reset_index()
    percentual = por_ano.mean().mul(100).reset_index()
    return contagem, percentual


def mostrar_cartoes_de_risco(contagem, percentual, ano_num, total_de_cenarios):
    linha_contagem = contagem[contagem["ano_num"] == ano_num].iloc[0]
    linha_percentual = percentual[percentual["ano_num"] == ano_num].iloc[0]
    for coluna_da_tela, evento in zip(st.columns(4), EVENTOS_ADVERSOS):
        with coluna_da_tela:
            st.metric(evento, numero_br(linha_percentual[evento], 1) + "%")
            st.caption(
                numero_br(linha_contagem[evento], 0)
                + " de "
                + numero_br(total_de_cenarios, 0)
                + " cenários"
            )


def montar_grafico_risco(percentual, ano_num):
    figura = go.Figure()
    for evento in EVENTOS_ADVERSOS:
        figura.add_trace(
            go.Scatter(
                x=percentual["ano_calendario"],
                y=percentual[evento],
                mode="lines+markers",
                line={"color": COR_DOS_EVENTOS[evento], "width": 4 if evento == EVENTOS_ADVERSOS[0] else 2},
                name=evento,
                hovertemplate=evento + ": %{y:,.1f}%<extra></extra>",
            )
        )
    eixo_y = {"title": "% dos cenários", "range": [-3, 103], "automargin": True}
    aplicar_estilo(figura, "% dos cenários em que o evento ocorre, por ano", 400, ano_num, eixo_y)
    return figura


def nota_de_risco(kpis):
    total = kpis["cenario"].nunique()
    texto = (
        "Percentuais sobre os "
        + numero_br(total, 0)
        + " cenários da CTI. 0% e 100% indicam eventos que ocorrem igual em todos os cenários."
    )

    caixa_zerado = kpis[kpis["saldo_final_caixa"] <= LIMITE_CAIXA_ZERADO]
    if not caixa_zerado.empty:
        primeiro = int(caixa_zerado["cenario_num"].min())
        ultimo = int(caixa_zerado["cenario_num"].max())
        texto = texto + f" Na base, os casos de caixa zerado estão nos cenários numerados de {primeiro} a {ultimo}."

    if (kpis["lucro_liquido"] < 0).sum() == 0 and (kpis["eva"] < 0).sum() == 0:
        texto = texto + " Prejuízo líquido e EVA negativo não ocorrem em nenhum cenário e ano."

    extremos = kpis.groupby("ano_num")["dfc_dividendos"].agg(["min", "max"])
    anos_com_dividendo_fixo = int(((extremos["max"] - extremos["min"]).abs() < 1).sum())
    texto = texto + f" Os dividendos pagos são iguais em todos os cenários em {anos_com_dividendo_fixo} dos 12 anos."
    return texto


def mostrar_risco(kpis, ano_num):
    st.subheader("Risco ao longo dos anos")
    st.write("Em quantos dos cenários cada evento acontece, ano a ano.")
    contagem, percentual = calcular_risco_por_ano(kpis)
    total_de_cenarios = kpis["cenario"].nunique()
    mostrar_cartoes_de_risco(contagem, percentual, ano_num, total_de_cenarios)
    st.plotly_chart(montar_grafico_risco(percentual, ano_num), key="grafico_risco")
    st.caption(nota_de_risco(kpis))
