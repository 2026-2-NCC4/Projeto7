"""
Seção "Top 10 cenários": ranking da planilha de Contabilidade, com a explicação do score e dois gráficos.
"""

import plotly.graph_objects as go
import streamlit as st

from configuracao import (
    ALIQUOTA_BASE,
    COR_DA_MEDIANA,
    METRICAS_DO_SCORE,
    PENALIDADE_POR_ANO_DE_RISCO,
    WACC_BASE,
)
from formatacao import escapar_cifrao, formatar, numero_br


def montar_tabela_do_score():
    linhas = ["| Métrica | Peso | Melhor quando | O que mede |", "|---|---|---|---|"]
    for metrica in METRICAS_DO_SCORE:
        linhas.append(
            "| " + metrica["nome"] + " | " + formatar(metrica["peso"], "%") + " | " + metrica["melhor"]
            + " | " + metrica["definicao"] + " |"
        )
    return "\n".join(linhas)


def mostrar_explicacao_do_score():
    penalidade = numero_br(PENALIDADE_POR_ANO_DE_RISCO * 100, 0) + "%"
    with st.expander("Como o score é calculado", expanded=True):
        st.markdown(
            "Cada cenário recebe uma nota de 0 a 1 em cada métrica: a posição dele entre os 1.200 cenários "
            "(1 é o melhor, 0 é o pior). Nas métricas em que menor é melhor, a nota é invertida. "
            "O score é a soma das notas multiplicadas pelos pesos abaixo, reduzida pela penalidade de anos-risco."
        )
        st.markdown("`Score = (soma de peso x nota) x (1 - " + penalidade + " x anos-risco)`")
        st.markdown(montar_tabela_do_score())
        st.markdown(
            "**Ano-risco:** cada ano com saldo de caixa negativo e cada ano com liquidez corrente abaixo de 1 "
            "contam um ano-risco (um ano com os dois conta dois). Cada ano-risco tira " + penalidade + " do score."
        )
        st.markdown(
            "**Premissas:** WACC de " + formatar(WACC_BASE, "%") + " e alíquota de IR e CS de " + formatar(ALIQUOTA_BASE, "%")
            + ". O capital investido é calculado com sinal: -(patrimônio líquido + empréstimos "
            "de curto e longo prazo), uma premissa do grupo. A base guarda passivo e patrimônio líquido com sinal "
            "negativo, e o passivo circulante muda de sinal em alguns anos: esses anos ficam fora das médias de LC, "
            "PCT e CE (entram de 4 a 11 anos por cenário). O ranking não muda com os controles da seção de sensibilidade."
        )


def montar_rotulos(ranking):
    rotulos = []
    for _, linha in ranking.iterrows():
        rotulos.append(str(linha["posicao"]) + "º - " + linha["cenario"])
    return rotulos


def montar_grafico_de_scores(ranking):
    textos = [numero_br(score, 3) for score in ranking["score"]]
    figura = go.Figure(
        go.Bar(
            x=ranking["score"],
            y=montar_rotulos(ranking),
            orientation="h",
            text=textos,
            textposition="outside",
            cliponaxis=False,
            marker={"color": COR_DA_MEDIANA},
            hovertemplate="%{y}<br>Score: %{text}<extra></extra>",
        )
    )
    figura.update_layout(
        title="Score do Top 10 (0 a 1)",
        height=420,
        separators=",.",
        margin={"l": 60, "r": 40, "t": 50, "b": 10},
        xaxis={"title": "Score", "range": [0, 1]},
        yaxis={"autorange": "reversed"},
    )
    return figura


def montar_grafico_valor_e_caixa(ranking):
    posicoes = [str(posicao) + "º" for posicao in ranking["posicao"]]
    figura = go.Figure(
        go.Scatter(
            x=ranking["caixa_minimo_mi"],
            y=ranking["vp_dos_evas_mi"],
            mode="markers+text",
            text=posicoes,
            textposition="top center",
            marker={"size": 14, "color": COR_DA_MEDIANA},
            customdata=ranking[["cenario", "score"]],
            hovertemplate=(
                "%{customdata[0]}<br>Score: %{customdata[1]:.3f}"
                "<br>Caixa mínimo: %{x:,.0f}<br>VP dos EVAs: %{y:,.0f}<extra></extra>"
            ),
        )
    )
    figura.update_layout(
        title="Valor criado e folga de caixa no Top 10 (o número é a posição no ranking)",
        height=440,
        separators=",.",
        margin={"l": 60, "r": 10, "t": 50, "b": 10},
        xaxis={"title": "Caixa mínimo (R$ milhões)", "automargin": True},
        yaxis={"title": "VP dos EVAs (R$ milhões)", "automargin": True},
    )
    return figura


def frase_valor_e_caixa(ranking):
    maior_valor = ranking.loc[ranking["vp_dos_evas_mi"].idxmax()]
    maior_caixa = ranking.loc[ranking["caixa_minimo_mi"].idxmax()]
    return escapar_cifrao(
        "Quanto mais alto, mais valor criado para o acionista; quanto mais à direita, mais folga de caixa. "
        "O maior VP dos EVAs do Top 10 é o do " + maior_valor["cenario"] + " (" + str(maior_valor["posicao"])
        + "º, R$ " + numero_br(maior_valor["vp_dos_evas_mi"], 0) + " mi) e o maior caixa mínimo é o do "
        + maior_caixa["cenario"] + " (" + str(maior_caixa["posicao"]) + "º, R$ "
        + numero_br(maior_caixa["caixa_minimo_mi"], 0) + " mi)."
    )


def mostrar_ranking(ranking):
    st.subheader("Top 10 cenários por score")
    st.markdown("**Quais cenários têm a melhor trajetória de 12 anos?**")
    st.write(
        "Ranking da planilha de Contabilidade: um score de 0 a 1 que combina criação de valor, rentabilidade, "
        "liquidez e endividamento. Ele vale para os 1.200 cenários e não muda com os filtros da barra lateral."
    )
    mostrar_explicacao_do_score()
    st.plotly_chart(montar_grafico_de_scores(ranking), key="grafico_ranking")
    st.plotly_chart(montar_grafico_valor_e_caixa(ranking), key="grafico_valor_e_caixa")
    st.caption(frase_valor_e_caixa(ranking))
