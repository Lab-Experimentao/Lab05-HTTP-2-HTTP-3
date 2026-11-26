# Coleta piloto

> Issue #10. 5 cargas por combinação (2 protocolos × 5 níveis de perda), 50 no total, em 26/11/2026.
> Dados: [piloto.csv](../dados/piloto.csv) e [piloto_rede.csv](../dados/piloto_rede.csv).

O piloto serve para validar a cadeia completa antes da coleta oficial. **Os dados dele não entram na análise final** (regra 6 do [plano de análise](plano-analise.md)).

## Como reproduzir

```
make up
make piloto
```

O `make piloto` mede as cargas ([medicao.md](medicao.md)) e roda o conferidor ([conferir.py](../analise/conferir.py)). Para conferir um CSV existente: `make conferir SAIDA=piloto.csv REPS=5`.

## Ambiente

| Item | Valor |
|---|---|
| Máquina | Apple M2, 8 núcleos, 24 GB, macOS 15.6.1 |
| Docker | 29.5.3 (kernel da VM 6.12.76-linuxkit) |
| Caddy | 2.11.9 |
| Google Chrome | 158.0.8127.88, **emulado em x86** (não há versão Linux ARM) |
| Playwright | 1.65.1 |

## O que foi conferido

| Verificação | Resultado |
|---|---|
| Cargas válidas por combinação | 5 em todas as 10 combinações |
| Protocolo usado = pedido, na página e em todos os recursos | sim, nas 50 cargas |
| Fallbacks | 0 |
| Falhas (timeout ou erro) | 0 |
| Recursos carregados | 40 em todas as cargas |
| Perda observada = configurada | sim, em todos os níveis (tabela abaixo) |

### Perda aplicada

Os contadores do `netem` no servidor são zerados antes de cada nível e lidos ao fim dele. A perda observada precisa ficar a até 3 erros padrão da configurada (binomial, pelo número de pacotes). Em 0%, nenhum pacote pode ser descartado.

| Perda configurada | Pacotes do servidor | Descartados | Perda observada | Esperado (±3 EP) |
|---:|---:|---:|---:|---|
| 0% | 16.276 | 0 | 0,00% | 0 |
| 1% | 15.480 | 162 | 1,05% | 0,76% a 1,24% |
| 2% | 15.758 | 297 | 1,88% | 1,67% a 2,33% |
| 3% | 15.763 | 436 | 2,77% | 2,59% a 3,41% |
| 5% | 16.105 | 827 | 5,14% | 4,48% a 5,52% |

## Resultados descritivos

Só para orientar a coleta completa. Com 5 cargas, não servem para estimar o efeito.

| Protocolo | Perda | Mediana do tempo de carga (ms) | CV | Mediana do TTFB (ms) |
|---|---:|---:|---:|---:|
| h2 | 0% | 829 | 10% | 168 |
| h3 | 0% | 733 | 4% | 152 |
| h2 | 1% | 7.110 | 6% | 169 |
| h3 | 1% | 5.294 | 19% | 151 |
| h2 | 2% | 7.803 | 7% | 169 |
| h3 | 2% | 6.035 | 19% | 148 |
| h2 | 3% | 11.396 | 16% | 166 |
| h3 | 3% | 8.838 | 11% | 150 |
| h2 | 5% | 18.234 | 14% | 221 |
| h3 | 5% | 12.742 | 7% | 152 |

CV = desvio padrão ÷ média do tempo de carga.

## O que isso muda para a coleta completa (#11)

- **Número de cargas: mantido em 90.** Em 0%, o CV ficou em 10% (h2) e 4% (h3), abaixo dos cerca de 15% a partir dos quais o plano de análise prevê que a equivalência de ±10% pode ficar inconclusiva. A estimativa é grosseira, com 5 cargas, mas não indica problema.
- **Falhas:** nenhuma. A simulação de poder supôs 5% de falhas como cenário pessimista, e o piloto não contradiz essa suposição.
- **Timeout de 60 s:** a carga mais lenta levou cerca de 21 s (h2, 5%), com folga.
- **Duração:** o piloto levou 8 min. Contando a abertura do Chrome, cada carga levou em média 3 s em 0%, 8 s em 1%, 9 s em 2%, 12 s em 3% e 18 s em 5%. Com 90 cargas por combinação, a coleta completa deve levar **cerca de 2,5 horas** nesta máquina.
- **Máquina:** a coleta completa deve rodar nesta mesma máquina, para que o piloto represente a coleta. A emulação x86 deixa as cargas mais lentas, e isso deve ser citado como limitação.

## Problemas encontrados e corrigidos

| Problema | Correção |
|---|---|
| Algumas cargas registravam 41 recursos: o Chrome pedia `/favicon.ico` sozinho (404) | favicon vazio na página (`<link rel="icon" href="data:,">`), feito na #8 |
| `make up` falhava em Mac ARM: o Google Chrome não tem versão Linux ARM | `platform: linux/amd64` no cliente, feito na #8 |
| Não havia como provar que a perda aplicada era a configurada | contadores do `netem` zerados e lidos em cada nível ([coletar.sh](../scripts/coletar.sh)) |
| Conferir o CSV à mão seria lento e sujeito a erro | [conferir.py](../analise/conferir.py), rodado ao fim de toda coleta |

## Para a discussão

O salto de 0% para 1% é grande nos dois protocolos: a carga passa de menos de 1 s para 5 a 7 s, enquanto de 1% para 2% muda pouco. Vale olhar isso na análise. Uma explicação possível é o custo de recuperar perdas com RTT de 50 ms, somado à emulação, mas o piloto não basta para afirmar a causa.
