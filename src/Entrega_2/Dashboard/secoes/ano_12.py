"""
Seção "Ano 12": do caixa inicial ao caixa final no encerramento da concessão e quanto vai para o acionista.
"""

import plotly.graph_objects as go
import streamlit as st

from componentes import mostrar_cartoes
from configuracao import (
    ANO_BASE,
    ANO_ENCERRAMENTO,
    COR_DE_AUMENTO,
    COR_DE_QUEDA,
    COR_DO_TOTAL,
    ITENS_DA_PONTE,
    KPIS_DO_ANO_12,
    OPCAO_MEDIANA,
    TITULO_DO_EIXO,
)
from dados import linha_de_percentis, valor_do_cenario
from formatacao import converter_para_exibicao, escapar_cifrao, formatar, numero_br

MEDIDAS_DA_PONTE = ["absolute", "relative", "relative", "relative", "relative", "absolute"]


def valores_da_ponte(percentis, kpis, cenario):
    valores = []
    for kpi in ITENS_DA_PONTE:
        if cenario == OPCAO_MEDIANA:
            valor = linha_de_percentis(percentis, kpi, ANO_ENCERRAMENTO)["p50"]
        else:
            valor = valor_do_cenario(kpis, cenario, ANO_ENCERRAMENTO, kpi)
        valores.append(converter_para_exibicao(valor, "R$"))
    return valores


def texto_da_barra(valor, medida):
    if medida == "absolute":
        return numero_br(valor, 0)
    sinal = "+" if valor >= 0 else "-"
    return sinal + numero_br(abs(valor), 0)


def montar_grafico_ponte(valores, catalogo, cenario):
    nomes = [catalogo.loc[kpi, "nome"] for kpi in ITENS_DA_PONTE]
    textos = [texto_da_barra(valor, medida) for valor, medida in zip(valores, MEDIDAS_DA_PONTE)]

    figura = go.Figure(
        go.Waterfall(
            x=nomes,
            y=valores,
            measure=MEDIDAS_DA_PONTE,
            text=textos,
            textposition="outside",
            cliponaxis=False,
            increasing={"marker": {"color": COR_DE_AUMENTO}},
            decreasing={"marker": {"color": COR_DE_QUEDA}},
            totals={"marker": {"color": COR_DO_TOTAL}},
            connector={"line": {"color": "gray", "width": 1}},
            hovertemplate="%{x}: %{text} (R$ milhões)<extra></extra>",
        )
    )
    figura.update_layout(
        title="Do caixa inicial ao caixa final em " + str(ANO_BASE + ANO_ENCERRAMENTO) + " - " + cenario,
        height=420,
        separators=",.",
        showlegend=False,
        margin={"l": 60, "r": 10, "t": 70, "b": 10},
        yaxis={"title": TITULO_DO_EIXO["R$"], "automargin": True},
    )
    return figura


def calcular_parcela_distribuida(kpis):
    ano_12 = kpis[kpis["ano_num"] == ANO_ENCERRAMENTO].set_index("cenario")
    caixa_disponivel = (
        ano_12["dfc_caixa_inicial"]
        + ano_12["dfc_fco"]
        + ano_12["dfc_investimentos"]
        + ano_12["dfc_juros_liquidos"]
    )
    return -ano_12["dfc_dividendos"] / caixa_disponivel


def frase_de_leitura(parcelas, cenario):
    mediana = formatar(parcelas.median(), "%")
    if cenario == OPCAO_MEDIANA:
        piso = formatar(parcelas.quantile(0.05), "%")
        teto = formatar(parcelas.quantile(0.95), "%")
        return (
            "No encerramento, o acionista recebe " + mediana + " do caixa disponível (mediana dos cenários). "
            "Em 90% dos cenários, essa parcela fica entre " + piso + " e " + teto + "."
        )

    parcela = parcelas[cenario]
    texto = (
        "No " + cenario + ", o acionista recebe " + formatar(parcela, "%")
        + " do caixa disponível no encerramento (mediana dos cenários: " + mediana + ")."
    )
    if parcela > 1:
        texto = texto + " A distribuição passa do caixa disponível e o caixa final fica negativo."
    return texto


def nota_da_ponte(valores, cenario):
    if cenario != OPCAO_MEDIANA:
        return ""
    soma_dos_itens = numero_br(sum(valores[:-1]), 0)
    caixa_final = numero_br(valores[-1], 0)
    return escapar_cifrao(
        "Na mediana, cada barra é a mediana do item nos 1.200 cenários, e a mediana não é aditiva: "
        "a soma dos itens dá R$ " + soma_dos_itens + " mi, e a mediana do caixa final é R$ " + caixa_final + " mi. "
        "Em um cenário específico, os itens somam exatamente o caixa final."
    )


def mostrar_ano_12(catalogo, percentis, kpis, cenario):
    st.subheader("Ano 12: encerramento da concessão (" + str(ANO_BASE + ANO_ENCERRAMENTO) + ")")
    st.caption("Esta seção mostra sempre o Ano 12, seja qual for o ano escolhido na barra lateral.")
    st.markdown("**Quanto caixa sobra no encerramento e quanto vai para o acionista?**")
    mostrar_cartoes(KPIS_DO_ANO_12, 3, catalogo, percentis, kpis, cenario, ANO_ENCERRAMENTO)

    parcelas = calcular_parcela_distribuida(kpis)
    st.write(frase_de_leitura(parcelas, cenario))

    valores = valores_da_ponte(percentis, kpis, cenario)
    st.plotly_chart(montar_grafico_ponte(valores, catalogo, cenario), key="grafico_ano_12")
    st.caption(
        "Caixa disponível = caixa inicial + caixa operacional (FCO) + investimentos + juros líquidos, "
        "antes dos dividendos."
    )
    nota = nota_da_ponte(valores, cenario)
    if nota:
        st.caption(nota)
