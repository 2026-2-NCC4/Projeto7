import pandas as pd

from configuracao import ANO_BASE


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


def escapar_cifrao(texto):
    return texto.replace("$", "\\$")


def rotulo_ano(ano_num):
    texto = f"{ANO_BASE + ano_num} (Ano {ano_num})"
    if ano_num == 12:
        texto = texto + " - encerramento"
    return texto


def converter_para_exibicao(valores, unidade):
    if unidade == "R$":
        return valores / 1e6
    if unidade == "%":
        return valores * 100
    return valores
