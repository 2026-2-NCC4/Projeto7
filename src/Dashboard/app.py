"""
Dados (src/Staging): kpis.parquet, kpi_catalogo.csv e percentis.csv.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
            st.caption("Faixa de 90% dos cenários: " + texto_faixa)
        else:
            diferenca = formatar_diferenca(valor - mediana, unidade) + " vs mediana"
            st.metric(nome, formatar(valor, unidade), delta=diferenca, delta_color=COR_DO_DELTA[direcao])
            texto = "Mediana: " + formatar(mediana, unidade) + " | faixa de 90%: " + texto_faixa
            if valor < faixa["p5"] or valor > faixa["p95"]:
                texto = texto + " | fora da faixa de 90%"
            st.caption(texto)


def mostrar_cartoes(lista_de_kpis, colunas_por_linha, catalogo, percentis, kpis, cenario, ano_num):
    for inicio in range(0, len(lista_de_kpis), colunas_por_linha):
        kpis_da_linha = lista_de_kpis[inicio:inicio + colunas_por_linha]
        colunas_da_tela = st.columns(colunas_por_linha)
        for coluna_da_tela, kpi in zip(colunas_da_tela, kpis_da_linha):
            mostrar_cartao(coluna_da_tela, kpi, catalogo, percentis, kpis, cenario, ano_num)


def converter_para_exibicao(valores, unidade):
    if unidade == "R$":
        return valores / 1e6
    if unidade == "%":
        return valores * 100
    return valores


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
        title=nome + " por ano",
        height=380,
        separators=",.",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2},
        margin={"l": 60, "r": 10, "t": 50, "b": 10},
        xaxis={"dtick": 1, "range": [ANO_BASE + 0.5, ANO_BASE + 12.5], "title": None},
        yaxis={"title": TITULO_DO_EIXO[unidade], "automargin": True},
    )
    return figura


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

    st.caption(
        "Fonte: CTI Global, projeção anonimizada (Ano 1 = 2027). A mediana é calculada por KPI "
        "e por ano e não corresponde a um cenário real. Valores em R$ milhões; margens em %."
    )


main()
