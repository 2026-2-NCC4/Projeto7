"""
Seção "Sensibilidade": como o EVA muda com o WACC e a alíquota, e o WACC em que a concessão deixa de criar valor.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from configuracao import (
    ALIQUOTA_BASE,
    COR_DA_FAIXA,
    COR_DA_MEDIANA,
    COR_DO_CENARIO,
    COR_DO_ESCOLHIDO,
    OPCAO_MEDIANA,
    TITULO_DO_EIXO,
    WACC_BASE,
)
from formatacao import converter_para_exibicao, escapar_cifrao, formatar, formatar_diferenca, numero_br

GRADE_DE_WACC = np.arange(4, 51, 1) / 100


def montar_matrizes(kpis):
    ebit = kpis.pivot(index="cenario", columns="ano_num", values="ebit")
    capital = kpis.pivot(index="cenario", columns="ano_num", values="capital_investido")
    return ebit.index, ebit.to_numpy(), capital.to_numpy()


def calcular_evas(ebit, capital, wacc, aliquota):
    return ebit * (1 - aliquota) - capital * wacc


def calcular_vp_dos_evas(ebit, capital, wacc, aliquota):
    anos = np.arange(1, ebit.shape[1] + 1)
    evas = calcular_evas(ebit, capital, wacc, aliquota)
    return (evas / (1 + wacc) ** anos).sum(axis=1)


def calcular_wacc_de_equilibrio(ebit, capital, aliquota):
    total = ebit.shape[0]
    piso = np.zeros((total, 1))
    teto = np.full((total, 1), 5.0)
    for _ in range(60):
        meio = (piso + teto) / 2
        vp = calcular_vp_dos_evas(ebit, capital, meio, aliquota).reshape(-1, 1)
        criando_valor = vp > 0
        piso = np.where(criando_valor, meio, piso)
        teto = np.where(criando_valor, teto, meio)
    return ((piso + teto) / 2).ravel()


def calcular_indicadores(cenarios, ebit, capital, wacc, aliquota):
    evas = calcular_evas(ebit, capital, wacc, aliquota)
    return {
        "eva_acumulado": pd.Series(evas.sum(axis=1), index=cenarios),
        "vp_dos_evas": pd.Series(calcular_vp_dos_evas(ebit, capital, wacc, aliquota), index=cenarios),
        "wacc_de_equilibrio": pd.Series(calcular_wacc_de_equilibrio(ebit, capital, aliquota), index=cenarios),
    }


def calcular_curva_do_vp(ebit, capital, aliquota):
    colunas = [calcular_vp_dos_evas(ebit, capital, wacc, aliquota) for wacc in GRADE_DE_WACC]
    return np.column_stack(colunas)


def mostrar_cartao_de_indicador(coluna_da_tela, nome, serie, unidade, cenario):
    mediana = serie.median()
    texto_faixa = formatar(serie.quantile(0.05), unidade) + " a " + formatar(serie.quantile(0.95), unidade)
    with coluna_da_tela:
        if cenario == OPCAO_MEDIANA:
            st.metric(nome, formatar(mediana, unidade))
            st.caption(escapar_cifrao("Faixa de 90% dos cenários: " + texto_faixa))
        else:
            valor = serie[cenario]
            diferenca = formatar_diferenca(valor - mediana, unidade) + " vs mediana"
            st.metric(nome, formatar(valor, unidade), delta=diferenca)
            st.caption(escapar_cifrao("Mediana: " + formatar(mediana, unidade) + " | faixa de 90%: " + texto_faixa))


def mostrar_cartao_de_perda(coluna_da_tela, eva_acumulado):
    total = len(eva_acumulado)
    negativos = int((eva_acumulado < 0).sum())
    with coluna_da_tela:
        st.metric("Cenários com EVA negativo", formatar(negativos / total, "%"))
        st.caption(
            numero_br(negativos, 0) + " de " + numero_br(total, 0) + " cenários com EVA acumulado negativo"
        )


def adicionar_marca_vertical(figura, x, nome, cor, tracado, y_minimo, y_maximo):
    figura.add_trace(
        go.Scatter(
            x=[x, x],
            y=[y_minimo, y_maximo],
            mode="lines",
            line={"color": cor, "dash": tracado, "width": 2},
            name=nome,
            hoverinfo="skip",
        )
    )


def montar_grafico_wacc(curva, cenarios, cenario, wacc, aliquota, wacc_de_equilibrio):
    grade = GRADE_DE_WACC * 100
    p5, p50, p95 = np.percentile(curva, [5, 50, 95], axis=0)
    p5 = converter_para_exibicao(p5, "R$")
    p50 = converter_para_exibicao(p50, "R$")
    p95 = converter_para_exibicao(p95, "R$")
    y_minimo = p5.min()
    y_maximo = p95.max()

    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=grade,
            y=p95,
            mode="lines",
            line={"width": 0},
            showlegend=False,
            hovertemplate="P95: %{y:,.0f}<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=grade,
            y=p5,
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor=COR_DA_FAIXA,
            name="Faixa de 90% (P5 a P95)",
            hovertemplate="P5: %{y:,.0f}<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=grade,
            y=p50,
            mode="lines",
            line={"color": COR_DA_MEDIANA},
            name="Mediana dos 1.200 cenários",
            hovertemplate="Mediana: %{y:,.0f}<extra></extra>",
        )
    )
    if cenario != OPCAO_MEDIANA:
        valores = converter_para_exibicao(curva[cenarios.get_loc(cenario)], "R$")
        y_minimo = min(y_minimo, valores.min())
        y_maximo = max(y_maximo, valores.max())
        figura.add_trace(
            go.Scatter(
                x=grade,
                y=valores,
                mode="lines",
                line={"color": COR_DO_CENARIO},
                name=cenario,
                hovertemplate=cenario + ": %{y:,.0f}<extra></extra>",
            )
        )

    figura.add_hline(y=0, line_color="gray", line_width=1)
    adicionar_marca_vertical(
        figura, WACC_BASE * 100, "Premissa (WACC " + formatar(WACC_BASE, "%") + ")", "gray", "dot", y_minimo, y_maximo
    )
    if abs(wacc - WACC_BASE) > 1e-9:
        nome = "WACC escolhido (" + formatar(wacc, "%") + ")"
        adicionar_marca_vertical(figura, wacc * 100, nome, COR_DO_ESCOLHIDO, "dash", y_minimo, y_maximo)
    nome = "WACC de equilíbrio (" + formatar(wacc_de_equilibrio, "%") + ")"
    adicionar_marca_vertical(figura, wacc_de_equilibrio * 100, nome, "black", "solid", y_minimo, y_maximo)

    figura.update_layout(
        title="VP dos EVAs conforme o WACC (alíquota de " + formatar(aliquota, "%") + ")",
        height=440,
        separators=",.",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.25, "traceorder": "normal"},
        margin={"l": 60, "r": 10, "t": 50, "b": 10},
        xaxis={"title": "WACC (% ao ano)", "range": [4, 50], "dtick": 5, "ticksuffix": "%", "hoverformat": ".0f"},
        yaxis={"title": TITULO_DO_EIXO["R$"], "automargin": True},
    )
    return figura


def frase_de_leitura(wacc_de_equilibrio, cenario):
    mediana = wacc_de_equilibrio.median()
    if cenario == OPCAO_MEDIANA:
        piso = formatar(wacc_de_equilibrio.quantile(0.05), "%")
        teto = formatar(wacc_de_equilibrio.quantile(0.95), "%")
        return (
            "A concessão só deixa de criar valor (VP dos EVAs abaixo de zero) com WACC acima de "
            + formatar(mediana, "%") + " ao ano (mediana dos cenários; em 90% deles, entre " + piso + " e " + teto
            + "), cerca de " + numero_br(mediana / WACC_BASE, 1) + " vezes a premissa de " + formatar(WACC_BASE, "%") + "."
        )

    return (
        "No " + cenario + ", a concessão só deixa de criar valor com WACC acima de "
        + formatar(wacc_de_equilibrio[cenario], "%") + " ao ano (mediana dos cenários: " + formatar(mediana, "%") + ")."
    )


def mostrar_sensibilidade(kpis, cenario):
    st.subheader("Sensibilidade: e se o custo de capital ou a alíquota mudarem?")
    st.markdown("**A concessão continua criando valor se o custo de capital subir?**")

    controles = st.columns(2)
    wacc = controles[0].slider(
        "WACC (% ao ano)", 4.0, 20.0, round(WACC_BASE * 100, 1), 0.5, format="%.1f", key="wacc_escolhido"
    ) / 100
    aliquota = controles[1].slider("Alíquota de IR e CS (%)", 25, 40, round(ALIQUOTA_BASE * 100), 1, key="aliquota_escolhida") / 100

    cenarios, ebit, capital = montar_matrizes(kpis)
    indicadores = calcular_indicadores(cenarios, ebit, capital, wacc, aliquota)
    eva_acumulado = indicadores["eva_acumulado"]
    wacc_de_equilibrio = indicadores["wacc_de_equilibrio"]

    primeira_linha = st.columns(3)
    mostrar_cartao_de_indicador(primeira_linha[0], "EVA acumulado", eva_acumulado, "R$", cenario)
    mostrar_cartao_de_indicador(primeira_linha[1], "VP dos EVAs", indicadores["vp_dos_evas"], "R$", cenario)
    mostrar_cartao_de_indicador(primeira_linha[2], "WACC de equilíbrio", wacc_de_equilibrio, "%", cenario)
    mostrar_cartao_de_perda(st.columns(3)[0], eva_acumulado)

    st.write(frase_de_leitura(wacc_de_equilibrio, cenario))

    if cenario == OPCAO_MEDIANA:
        equilibrio_exibido = wacc_de_equilibrio.median()
    else:
        equilibrio_exibido = wacc_de_equilibrio[cenario]
    curva = calcular_curva_do_vp(ebit, capital, aliquota)
    figura = montar_grafico_wacc(curva, cenarios, cenario, wacc, aliquota, equilibrio_exibido)
    st.plotly_chart(figura, key="grafico_sensibilidade")

    eva_base = calcular_evas(ebit, capital, WACC_BASE, ALIQUOTA_BASE).sum(axis=1)
    vp_base = calcular_vp_dos_evas(ebit, capital, WACC_BASE, ALIQUOTA_BASE)
    st.caption(
        escapar_cifrao(
            "Premissas da planilha (WACC " + formatar(WACC_BASE, "%") + ", alíquota " + formatar(ALIQUOTA_BASE, "%")
            + "): EVA acumulado mediano de " + formatar(np.median(eva_base), "R$")
            + " e VP dos EVAs mediano de " + formatar(np.median(vp_base), "R$") + "."
        )
    )
    st.caption(
        "EVA do ano = EBIT x (1 - alíquota) - capital investido x WACC. VP dos EVAs = soma do EVA de cada ano "
        "dividido por (1 + WACC) elevado ao número do ano (Anos 1 a 12). WACC de equilíbrio = taxa em que o VP dos EVAs "
        "fica igual a zero."
    )
    st.caption(
        "O capital investido é calculado com sinal: -(patrimônio líquido + empréstimos de curto e longo prazo). "
        "É uma premissa do grupo e o resultado depende dela."
    )
