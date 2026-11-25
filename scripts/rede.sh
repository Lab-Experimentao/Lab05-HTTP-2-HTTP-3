#!/bin/sh
# Roda dentro de cada container (ver "rede" no Makefile).
# Uso: rede.sh aplicar <perda %> | limpar | status
set -e
IF=eth0
ATRASO=25ms # em cada lado: RTT de 50 ms

case "$1" in
  aplicar)
    case "$2" in
      0|1|2|3|5) ;;
      *) echo "Perda inválida: '$2' (use 0, 1, 2, 3 ou 5)" >&2; exit 1 ;;
    esac
    # Sem isso o netem descarta blocos de vários pacotes TCP de uma vez.
    ip link set "$IF" gso_max_segs 1
    tc qdisc replace dev "$IF" root netem limit 10000 delay "$ATRASO" loss "$2%"
    ;;
  limpar)
    if tc qdisc show dev "$IF" | grep -q netem; then tc qdisc del dev "$IF" root; fi
    ;;
  status)
    tc -s qdisc show dev "$IF"
    ;;
  *) echo "Uso: rede.sh aplicar <0|1|2|3|5> | limpar | status" >&2; exit 1 ;;
esac
