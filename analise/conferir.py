"""Confere um CSV de coleta (issues #10 e #11). Uso: python analise/conferir.py dados/piloto.csv 5

Verifica, para cada combinação (protocolo, perda):
- se há o número esperado de cargas válidas (sem fallback);
- se o protocolo usado é o pedido em todas as linhas;
- se todas as cargas que não falharam carregaram os 40 recursos;
- se a perda observada no servidor (dados/<nome>_rede.csv) bate com a configurada.

Também mostra falhas, medianas e o CV (desvio padrão / média) do tempo de carga, que o
plano de análise pede para acompanhar no piloto. Sai com código 1 se algo não confere.
"""

import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RECURSOS = 40
PERDAS = (0, 1, 2, 3, 5)


def pct(x):
    return f"{100 * x:.2f}%".replace(".", ",")


def main(caminho, reps):
    caminho = Path(caminho)
    linhas = list(csv.DictReader(caminho.open(encoding="utf-8")))
    problemas = []

    grupos = defaultdict(list)
    for linha in linhas:
        grupos[(linha["protocolo_pedido"], int(linha["perda_pct"]))].append(linha)

    print(f"{caminho}: {len(linhas)} linhas\n")
    print("| protocolo | perda | válidas | fallbacks | falhas | mediana (ms) | CV | TTFB mediano (ms) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for perda in PERDAS:
        for protocolo in ("h2", "h3"):
            g = grupos.get((protocolo, perda), [])
            validas = [l for l in g if l["fallback"] == "0"]
            fallbacks = len(g) - len(validas)
            falhas = [l for l in validas if l["falhou"] == "1"]
            ok = [l for l in validas if l["falhou"] == "0"]
            tempos = [float(l["tempo_carga_ms"]) for l in ok]
            ttfbs = [float(l["ttfb_ms"]) for l in ok]

            if not g:
                continue
            if len(validas) != reps:
                problemas.append(f"{protocolo} {perda}%: {len(validas)} cargas válidas, esperado {reps}")
            reps_vistas = sorted(int(l["repeticao"]) for l in validas)
            if reps_vistas != list(range(1, len(validas) + 1)):
                problemas.append(f"{protocolo} {perda}%: repetições {reps_vistas}")
            for l in ok:
                if l["protocolo_usado"] != protocolo:
                    problemas.append(f"{protocolo} {perda}% rep {l['repeticao']}: usou {l['protocolo_usado']}")
                if int(l["recursos"]) != RECURSOS:
                    problemas.append(f"{protocolo} {perda}% rep {l['repeticao']}: {l['recursos']} recursos")

            mediana = f"{statistics.median(tempos):,.0f}" if tempos else "-"
            cv = f"{statistics.stdev(tempos) / statistics.mean(tempos):.0%}" if len(tempos) > 1 else "-"
            ttfb = f"{statistics.median(ttfbs):,.0f}" if ttfbs else "-"
            print(f"| {protocolo} | {perda}% | {len(validas)} | {fallbacks} | {len(falhas)} "
                  f"| {mediana} | {cv} | {ttfb} |".replace(",", "."))

    for (protocolo, perda) in grupos:
        if perda not in PERDAS or protocolo not in ("h2", "h3"):
            problemas.append(f"combinação inesperada: {protocolo} {perda}%")

    rede = caminho.with_name(caminho.stem + "_rede.csv")
    if rede.exists():
        print("\n| perda configurada | pacotes do servidor | descartados | perda observada | esperado (±3 EP) |")
        print("|---:|---:|---:|---:|---|")
        for l in csv.DictReader(rede.open(encoding="utf-8")):
            perda, n, d = int(l["perda_pct"]), int(l["pacotes"]), int(l["descartados"])
            p = perda / 100
            margem = 3 * math.sqrt(p * (1 - p) / n) if n else 0  # erro padrão binomial
            obs = d / n if n else 0
            confere = abs(obs - p) <= margem if perda else d == 0
            faixa = f"{pct(p - margem)} a {pct(p + margem)}" if perda else "0"
            pacotes = f"{n:,}".replace(",", ".")
            print(f"| {perda}% | {pacotes} | {d} | {pct(obs)} | {faixa}{'' if confere else ' **NÃO CONFERE**'} |")
            if not confere:
                problemas.append(f"perda {perda}%: observada {pct(obs)}")
    else:
        problemas.append(f"{rede} não encontrado: perda aplicada não conferida")

    print()
    if problemas:
        print("PROBLEMAS:")
        for p in problemas:
            print(f"- {p}")
        sys.exit(1)
    print("Tudo confere.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: python analise/conferir.py <arquivo.csv> <reps>")
    main(sys.argv[1], int(sys.argv[2]))
