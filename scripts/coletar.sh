#!/bin/sh
# Roda no host (ver "coleta" no Makefile).
# Uso: coletar.sh <reps> <saida.csv> <semente> <perdas...>
# Para cada nível: zera as regras, aplica a perda, mede e grava a perda observada no servidor
# em dados/<saida>_rede.csv (pacotes que saíram do servidor e quantos o netem descartou).
set -e
REPS=$1; SAIDA=$2; SEMENTE=$3; shift 3
REDE="dados/$(basename "$SAIDA" .csv)_rede.csv"
mkdir -p dados
[ -s "$REDE" ] || echo "perda_pct,pacotes,descartados,perda_observada_pct" > "$REDE"

for p in "$@"; do
  make --no-print-directory rede-limpar # zera os contadores do netem
  make --no-print-directory rede PERDA="$p"
  docker compose exec -T client node medir.js --perda "$p" --reps "$REPS" \
    --saida "/dados/$SAIDA" --semente "$SEMENTE"
  docker compose exec -T server tc -s qdisc show dev eth0 | awk -v p="$p" '
    /Sent/ {
      for (i = 1; i <= NF; i++) { if ($i == "pkt") enviados = $(i - 1); if ($i == "(dropped") descartados = $(i + 1) }
      sub(/,/, "", descartados)
      total = enviados + descartados
      printf "%s,%d,%d,%.2f\n", p, total, descartados, total ? 100 * descartados / total : 0
      exit
    }' | tee -a "$REDE"
done
make --no-print-directory rede-limpar
