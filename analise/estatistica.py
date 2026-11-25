"""Estatística do experimento. h2 e h3 são vetores de tempos (ms) de um mesmo nível de perda."""

import numpy as np
from scipy import stats

ALPHA = 0.05
PIOR_VALOR = 1e12  # tempo atribuído a uma carga que falhou: fica em último no ranking


def alternativa(metrica, perda):
    """GQM 6.2 e 6.4: só o tempo de carga com perda é unilateral (h3 menor que h2)."""
    return "less" if metrica == "tempo_carga_ms" and perda > 0 else "two-sided"


def com_falhas(tempos, falhou):
    """Troca o tempo das cargas que falharam pelo pior valor, em vez de descartá-las."""
    return np.where(falhou, PIOR_VALOR, tempos)


def mann_whitney(h2, h3, alternative="two-sided"):
    """p-valor; aceita matrizes simulações × observações."""
    return stats.mannwhitneyu(h3, h2, axis=-1, alternative=alternative, method="asymptotic").pvalue


def cliff_delta(h2, h3):
    """P(h2 > h3) - P(h2 < h3): positivo quando o HTTP/3 é mais rápido."""
    return float(np.sign(np.subtract.outer(h2, h3)).mean())


def holm(p):
    """p-valores ajustados por Holm no último eixo."""
    p = np.asarray(p, dtype=float)
    m = p.shape[-1]
    ordem = np.argsort(p, axis=-1)
    ajustado = np.take_along_axis(p, ordem, -1) * (m - np.arange(m))
    ajustado = np.minimum(np.maximum.accumulate(ajustado, axis=-1), 1)
    saida = np.empty_like(p)
    np.put_along_axis(saida, ordem, ajustado, -1)
    return saida


def fisher(falhas_h2, n_h2, falhas_h3, n_h3):
    """p-valor bilateral da diferença entre as taxas de falha."""
    tabela = [[falhas_h2, n_h2 - falhas_h2], [falhas_h3, n_h3 - falhas_h3]]
    return float(stats.fisher_exact(tabela).pvalue)


def ponto_de_virada(perdas, rejeita):
    """GQM 6.3: menor perda (> 0) rejeitada em que todas as maiores também são. None se não há."""
    virada = None
    for perda, r in sorted(zip(perdas, rejeita), reverse=True):
        if perda == 0 or not r:
            break
        virada = perda
    return virada


def _medianas_bootstrap(x, reamostras, rng):
    return np.median(x[rng.integers(0, len(x), (reamostras, len(x)))], axis=1)


def ic_diferenca_medianas(h2, h3, rng, reamostras=10_000, confianca=0.95):
    """IC de mediana(h2) - mediana(h3), por bootstrap percentil."""
    d = _medianas_bootstrap(h2, reamostras, rng) - _medianas_bootstrap(h3, reamostras, rng)
    return np.quantile(d, [(1 - confianca) / 2, (1 + confianca) / 2])


def equivalentes(h2, h3, rng, margem=0.10, reamostras=10_000, alpha=ALPHA):
    """TOST: o IC de 1 - 2α da razão das medianas (h3/h2) cabe em 1 ± margem?"""
    razao = _medianas_bootstrap(h3, reamostras, rng) / _medianas_bootstrap(h2, reamostras, rng)
    baixo, alto = np.quantile(razao, [alpha, 1 - alpha])
    return bool(1 - margem < baixo and alto < 1 + margem)
