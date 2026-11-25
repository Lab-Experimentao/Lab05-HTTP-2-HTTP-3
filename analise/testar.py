"""Confere as funções contra valores conhecidos. Uso: python analise/testar.py"""

import numpy as np

from estatistica import (
    PIOR_VALOR, alternativa, cliff_delta, com_falhas, equivalentes, fisher, holm,
    ic_diferenca_medianas, mann_whitney, ponto_de_virada,
)

lento, rapido = np.arange(100.0, 130), np.arange(0.0, 30)
rng = np.random.default_rng(42)

assert cliff_delta(lento, rapido) == 1 and cliff_delta(rapido, lento) == -1
assert cliff_delta(lento, lento) == 0
assert mann_whitney(lento, rapido, "less") < 0.001 and mann_whitney(rapido, lento, "less") > 0.99
assert np.allclose(holm([0.01, 0.04, 0.03, 0.005]), [0.03, 0.06, 0.06, 0.02])
assert abs(fisher(3, 4, 1, 4) - 0.4857) < 1e-4  # experimento da dama do chá
perdas = [0, 1, 2, 3, 5]
assert ponto_de_virada(perdas, [False, False, True, True, True]) == 2
assert ponto_de_virada(perdas, [False, True, False, False, True]) == 5
assert ponto_de_virada(perdas, [False] * 5) is None
assert ponto_de_virada(perdas, [True] * 5) == 1
assert alternativa("tempo_carga_ms", 0) == alternativa("ttfb_ms", 5) == "two-sided"
assert alternativa("tempo_carga_ms", 1) == "less"
assert list(com_falhas(np.array([5.0, 7]), np.array([False, True]))) == [5, PIOR_VALOR]
baixo, alto = ic_diferenca_medianas(lento, rapido, rng)
assert baixo < 100 < alto
assert equivalentes(lento, lento, rng) and not equivalentes(lento, lento * 1.5, rng)
print("OK")
