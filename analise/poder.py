"""Simulação de poder para o nº de repetições por combinação. Uso: python analise/poder.py"""

import csv
import zlib
from pathlib import Path

import numpy as np

from estatistica import ALPHA, PIOR_VALOR, equivalentes, holm, mann_whitney

SEED = 42
SIMULACOES = 10_000
SIMULACOES_TOST, REAMOSTRAS_TOST = 1_000, 500  # o bootstrap dentro da simulação é caro
NS = range(10, 121, 10)
DELTAS = (0, 0.147, 0.33, 0.474)
ALPHA_HOLM = ALPHA / 5  # 1º limiar de Holm com 5 níveis: o caso mais exigente
CVS = (0.05, 0.10, 0.15, 0.20, 0.30)
MARGENS = (0.05, 0.10)
CENARIOS = ("lognormal", "cauda pesada", "variâncias diferentes", "5% de falhas")
# Cliff's delta verdadeiro em 0, 1, 2, 3 e 5% de perda
PERFIS = {
    "sem efeito": (0, 0, 0, 0, 0),
    "virada em 2%, constante": (0, 0, 0.33, 0.33, 0.33),
    "virada em 2%, crescente": (0, 0, 0.33, 0.474, 0.6),
}
PASTA = Path(__file__).parent / "resultados"


def gerador(*chave):
    # Cada configuração tem a própria semente: incluir uma não altera as outras
    return np.random.default_rng([SEED, zlib.crc32(repr(chave).encode())])


def sortear_log(cenario, grupo, forma, rng):
    if cenario == "cauda pesada":
        return rng.standard_t(3, forma)
    return rng.normal(0, 1.5 if cenario == "variâncias diferentes" and grupo == "h2" else 1, forma)


def deslocamento(cenario, delta):
    """Quanto subtrair do log de h3 para que o Cliff's delta seja o pedido."""
    if delta == 0:
        return 0.0  # as distribuições são simétricas em torno de 0
    rng = gerador("deslocamento", cenario)
    h2, h3 = (sortear_log(cenario, g, 1_000_000, rng) for g in ("h2", "h3"))
    return np.quantile(h3 - h2, (1 + delta) / 2)


def gerar(cenario, d, forma, rng):
    # O Mann-Whitney só usa a ordem dos valores: trabalhar no log não muda o resultado
    h2 = sortear_log(cenario, "h2", forma, rng)
    h3 = sortear_log(cenario, "h3", forma, rng) - d
    if cenario == "5% de falhas":
        h2[rng.random(forma) < 0.05] = PIOR_VALOR
        h3[rng.random(forma) < 0.05] = PIOR_VALOR
    return h2, h3


def poder_por_teste():
    linhas = []
    for cenario in CENARIOS:
        for delta in DELTAS:
            d = deslocamento(cenario, delta)
            for n in NS:
                h2, h3 = gerar(cenario, d, (SIMULACOES, n), gerador(cenario, delta, n))
                uni, bi = (mann_whitney(h2, h3, a) for a in ("less", "two-sided"))
                linhas.append({
                    "cenario": cenario, "delta": delta, "n": n,
                    "unilateral_005": (uni < ALPHA).mean(), "bilateral_005": (bi < ALPHA).mean(),
                    "unilateral_001": (uni < ALPHA_HOLM).mean(), "bilateral_001": (bi < ALPHA_HOLM).mean(),
                })
    return linhas


def ponto_de_virada_com_holm():
    linhas = []
    for perfil, deltas in PERFIS.items():
        ds = [deslocamento("lognormal", x) for x in deltas]
        com_efeito = np.array(deltas) > 0
        for n in NS:
            rng = gerador(perfil, n)
            p = np.stack([
                mann_whitney(*gerar("lognormal", d, (SIMULACOES, n), rng), "less" if i else "two-sided")
                for i, d in enumerate(ds)
            ], axis=-1)
            rejeita = holm(p) < ALPHA
            tem = com_efeito.any()
            # A virada em 2% exige rejeitar 2, 3 e 5% e não rejeitar 1%; o 0% não participa
            linhas.append({
                "perfil": perfil, "n": n,
                "erro_familia": rejeita[:, ~com_efeito].any(axis=1).mean(),
                "todos_com_efeito": rejeita[:, com_efeito].all(axis=1).mean() if tem else "",
                "virada_exata": (rejeita[:, 1:] == com_efeito[1:]).all(axis=1).mean() if tem else "",
            })
    return linhas


def equivalencia():
    linhas = []
    for cv in CVS:
        sigma = np.sqrt(np.log(1 + cv**2))
        for margem in MARGENS:
            for n in NS:
                rng = gerador("tost", cv, margem, n)
                acertos = [
                    equivalentes(*np.exp(rng.normal(0, sigma, (2, n))), rng, margem, REAMOSTRAS_TOST)
                    for _ in range(SIMULACOES_TOST)
                ]
                linhas.append({"cv": cv, "margem": margem, "n": n, "poder": np.mean(acertos)})
    return linhas


def salvar(nome, linhas):
    with open(PASTA / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, linhas[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


if __name__ == "__main__":
    PASTA.mkdir(exist_ok=True)
    salvar("poder.csv", poder_por_teste())
    salvar("ponto_de_virada.csv", ponto_de_virada_com_holm())
    salvar("equivalencia.csv", equivalencia())
    print(f"Resultados em {PASTA}")
