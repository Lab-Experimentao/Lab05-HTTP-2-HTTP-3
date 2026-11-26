# Medição das cargas

O script [medir.js](../client/medir.js) roda no container cliente, carrega a página de teste ([pagina.md](pagina.md)) e grava uma linha por carga num CSV. O `Makefile` aplica a perda e chama o script em cada nível:

| Comando | O que faz |
|---|---|
| `make piloto` | 5 cargas por combinação em `dados/piloto.csv` (issue #10) |
| `make coleta` | 90 cargas por combinação em `dados/coleta.csv` (issue #11) |
| `make coleta REPS=2 PERDAS="0 5" SAIDA=teste.csv` | exemplo de coleta menor, para testar |

O CSV é aberto em modo de acréscimo: rodar de novo com o mesmo `SAIDA` adiciona linhas em vez de apagar as anteriores.

## Como cada carga é feita

| Decisão | Como | Por quê |
|---|---|---|
| Estado limpo | um Chrome novo por carga | nenhuma carga reaproveita cache, conexão, sessão TLS ou `alt-svc` da anterior |
| Protocolo | flags de [browser.js](../client/browser.js) (issue #6) | força h2 ou h3 desde a primeira requisição |
| Fim da carga | espera o `load` e depois `loadEventEnd > 0` | `loadEventEnd` só é preenchido depois do evento `load` |
| Métricas | Navigation Timing: `loadEventEnd − startTime` (M1) e `responseStart − startTime` (M2) | definição do [GQM](gqm-hipoteses.md), seção 4 |
| Protocolo usado | `nextHopProtocol` da navegação e de todos os recursos | se algum recurso vier por outro protocolo, a carga não é pura |
| Timeout | 60 s por carga (`--timeout`) | bem acima das cargas mais lentas observadas com 5% de perda (cerca de 20 s) |
| Falha | timeout, erro de navegação ou `load` que não acontece | definição do GQM (M3). A falha é gravada e a execução continua |
| Fallback | pediu um protocolo e veio outro: a linha é gravada com `fallback=1` e a carga é refeita, até 3 vezes | regra 2 do [plano de análise](plano-analise.md) |

## Ordem das cargas

Em cada nível de perda, as cargas de h2 e h3 são embaralhadas com uma semente fixa (`SEMENTE`, padrão 42, a mesma do plano de análise), combinada com o nível de perda. A mesma semente gera sempre a mesma ordem.

Os níveis de perda rodam em blocos (0, 1, 2, 3 e 5%), porque trocar a regra do `netem` a cada carga exigiria mudar a rede no servidor entre uma carga e outra. Isso não enviesa a análise, que sempre compara h2 com h3 dentro do mesmo nível. Dentro de cada bloco, a ordem aleatória evita que uma variação da máquina ao longo do tempo se confunda com o efeito do protocolo.

## Colunas do CSV

| Coluna | Conteúdo |
|---|---|
| `protocolo_pedido` | `h2` ou `h3` (variável independente) |
| `protocolo_usado` | `nextHopProtocol`. Se os recursos vieram por mais de um protocolo, aparecem todos, por exemplo `h3+h2`. Vazio quando a carga falhou |
| `perda_pct` | 0, 1, 2, 3 ou 5 (variável independente) |
| `repeticao` | 1 a `REPS`, por protocolo e nível. Uma carga refeita por fallback repete o número |
| `tempo_carga_ms` | M1. Vazio quando a carga falhou |
| `ttfb_ms` | M2. Vazio quando a carga falhou |
| `falhou` | 1 se a carga falhou, 0 se não (M3) |
| `fallback` | 1 se o protocolo usado diferiu do pedido. **Essas linhas saem da análise** |
| `recursos` | quantos recursos a página carregou (o esperado é 40) |
| `ordem` | posição da carga dentro do bloco do nível de perda |
| `inicio` | horário de início da carga (UTC) |
| `erro` | primeira linha da mensagem de erro, quando há falha |

## Mac com chip Apple

O Google Chrome não tem versão Linux ARM, então o cliente é sempre construído para x86 (`platform: linux/amd64` no [docker-compose.yml](../docker-compose.yml)). Num Mac ARM ele roda emulado: funciona, mas as cargas ficam mais lentas e variam mais. Por isso o piloto e a coleta completa devem rodar na mesma máquina, e essa máquina deve ser registrada na issue #11.
