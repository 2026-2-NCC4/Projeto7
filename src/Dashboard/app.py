"""
Dashboard Grafix (case CTI Global): monta a página e chama uma função por seção.
"""

import streamlit as st

from configuracao import OPCAO_MEDIANA
from dados import carregar_catalogo, carregar_kpis, carregar_percentis
from formatacao import rotulo_ano
from secoes.perspectivas import mostrar_perspectivas
from secoes.risco import mostrar_risco


def mostrar_filtros(kpis):
    st.sidebar.header("Filtros")
    cenarios = [OPCAO_MEDIANA] + sorted(kpis["cenario"].unique())
    cenario = st.sidebar.selectbox("Cenário", cenarios)
    ano_num = st.sidebar.selectbox("Ano", list(range(1, 13)), index=4, format_func=rotulo_ano)
    return cenario, ano_num


def mostrar_cabecalho(cenario, ano_num):
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


def main():
    st.set_page_config(page_title="Grafix - CTI", layout="wide")

    kpis = carregar_kpis()
    catalogo = carregar_catalogo()
    percentis = carregar_percentis()

    cenario, ano_num = mostrar_filtros(kpis)
    mostrar_cabecalho(cenario, ano_num)
    mostrar_perspectivas(catalogo, percentis, kpis, cenario, ano_num)
    mostrar_risco(kpis, ano_num)

    st.caption(
        "Fonte: CTI Global, projeção anonimizada (Ano 1 = 2027). A mediana é calculada por KPI "
        "e por ano e não corresponde a um cenário real. Valores em R$ milhões; margens em %."
    )


main()
