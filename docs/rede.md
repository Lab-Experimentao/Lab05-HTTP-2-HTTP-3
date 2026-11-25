# Emulação da rede (`tc netem`)

O script [rede.sh](../scripts/rede.sh) roda dentro de cada container e é chamado pelo `Makefile`:

| Comando | O que faz |
|---|---|
| `make rede PERDA=2` | aplica a perda (0, 1, 2, 3 ou 5%) e o atraso |
| `make rede-limpar` | remove as regras entre as rodadas |
| `make rede-status` | mostra as regras e os pacotes descartados |
| `make test-rede` | testa os 5 níveis com `ping` e Chrome |

## Configuração

| Item | Valor | Motivo |
|---|---|---|
| Perda | só na saída do servidor | é o sentido dos dados da página; explicação na seção 5.1 de [gqm-hipoteses.md](gqm-hipoteses.md) |
| Atraso | 25 ms na saída de cada container (RTT de 50 ms) | sem atraso, o RTT entre containers é menor que 0,1 ms e recuperar um pacote quase não custaria tempo. Os 50 ms são uma escolha do grupo, fixa em todos os níveis, e não a medição de uma rede específica |
| Tipo de perda | aleatória e independente | simples; não reproduz rajadas |
| Fila | 10000 pacotes | evita descartes além da perda configurada |
| Banda | sem limite | fora do escopo |

## Um pacote por vez

Por padrão, o Linux (TCP) e o Caddy (QUIC) entregam vários pacotes juntos à fila, num bloco só, e o `netem` descarta o bloco inteiro. Como o agrupamento difere entre TCP e QUIC, isso distorceria a comparação. Por isso ele é desligado:

- **HTTP/2:** `ip link set eth0 gso_max_segs 1` (no `rede.sh`).
- **HTTP/3:** `QUIC_GO_DISABLE_GSO=true` no servidor (no `docker-compose.yml`).

Maior média de bytes por pacote observada na fila do `netem`, baixando 5 MB:

| | HTTP/2 | HTTP/3 |
|---|---|---|
| Padrão | 10.065 | 8.804 |
| Com o ajuste | 1.514 | 1.421 |

Desligar só com `ethtool -K eth0 tso off gso off` não funcionou em nenhum dos dois.

O ajuste do HTTP/2 vale a partir do primeiro `make rede`; por isso, o nível de 0% também deve ser aplicado com `make rede PERDA=0`, e não deixando a rede sem regras.

## Validação (25/11/2026)

2000 pings por nível, RTT médio de 50,2 ms em todos. Descartes no servidor durante um download de 5 MB:

| Perda configurada | Perda no `ping` | Descartados, HTTP/2 | Descartados, HTTP/3 |
|---|---|---|---|
| 0% | 0% | 0 | 0 |
| 1% | 1,35% | 23 | 40 |
| 2% | 2,30% | 64 | 70 |
| 3% | 3,45% | 124 | 117 |
| 5% | 5,20% | 189 | 195 |

O Chrome carregou a página provisória em `h2` e em `h3` em todos os níveis.

## Limitações

- A perda no sentido cliente → servidor não é emulada.
- Não há rajadas de perda, limite de banda nem variação do atraso.
- Sem agrupamento de pacotes, o uso de CPU difere do de um servidor em produção.
