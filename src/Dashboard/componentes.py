
import pandas as pd
import streamlit as st

from configuracao import ANO_BASE, COR_DO_DELTA, OPCAO_MEDIANA
from dados import linha_de_percentis, valor_do_cenario
from formatacao import escapar_cifrao, formatar, formatar_diferenca


def mostrar_cartao(coluna_da_tela, kpi, catalogo, percentis, kpis, cenario, ano_num):
    nome = catalogo.loc[kpi, "nome"]
    unidade = catalogo.loc[kpi, "unidade"]
    direcao = catalogo.loc[kpi, "direcao"]

    faixa = linha_de_percentis(percentis, kpi, ano_num)
    mediana = faixa["p50"]

    with coluna_da_tela:
        if cenario == OPCAO_MEDIANA:
            valor = mediana
        else:
            valor = valor_do_cenario(kpis, cenario, ano_num, kpi)

        if pd.isna(valor) or pd.isna(mediana):
            st.metric(nome, "n/d")
            st.caption("Sem valor neste ano: a conta não existe no encerramento da concessão.")
            return

        texto_faixa = formatar(faixa["p5"], unidade) + " a " + formatar(faixa["p95"], unidade)
        if cenario == OPCAO_MEDIANA:
            st.metric(nome, formatar(mediana, unidade))
            st.caption(escapar_cifrao("Faixa de 90% dos cenários: " + texto_faixa))
        else:
            diferenca = formatar_diferenca(valor - mediana, unidade) + " vs mediana"
            st.metric(nome, formatar(valor, unidade), delta=diferenca, delta_color=COR_DO_DELTA[direcao])
            texto = "Mediana: " + formatar(mediana, unidade) + " | faixa de 90%: " + texto_faixa
            if valor < faixa["p5"] or valor > faixa["p95"]:
                texto = texto + " | fora da faixa de 90%"
            st.caption(escapar_cifrao(texto))


def mostrar_cartoes(lista_de_kpis, colunas_por_linha, catalogo, percentis, kpis, cenario, ano_num):
    for inicio in range(0, len(lista_de_kpis), colunas_por_linha):
        kpis_da_linha = lista_de_kpis[inicio:inicio + colunas_por_linha]
        colunas_da_tela = st.columns(colunas_por_linha)
        for coluna_da_tela, kpi in zip(colunas_da_tela, kpis_da_linha):
            mostrar_cartao(coluna_da_tela, kpi, catalogo, percentis, kpis, cenario, ano_num)


def aplicar_estilo(figura, titulo, altura, ano_num, eixo_y):
    figura.add_vrect(
        x0=ANO_BASE + 11.5,
        x1=ANO_BASE + 12.5,
        fillcolor="gray",
        opacity=0.12,
        line_width=0,
        annotation_text="encerramento",
        annotation_position="top left",
        annotation_textangle=-90,
    )
    figura.add_vline(x=ANO_BASE + ano_num, line_dash="dot", line_color="gray")
    figura.update_layout(
        title=titulo,
        height=altura,
        separators=",.",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2},
        margin={"l": 60, "r": 10, "t": 50, "b": 10},
        xaxis={"dtick": 1, "range": [ANO_BASE + 0.5, ANO_BASE + 12.5], "title": None},
        yaxis=eixo_y,
    )
