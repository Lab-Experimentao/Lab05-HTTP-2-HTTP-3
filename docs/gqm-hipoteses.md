# Pergunta de pesquisa, GQM e hipóteses

## 1. Pergunta de pesquisa

**A partir de qual nível de perda de pacotes o HTTP/3 carrega uma página mais rápido que o HTTP/2? E em redes boas, existe diferença?**

A pergunta tem duas partes, que são tratadas de forma diferente:

- **Parte 1 (redes ruins):** procurar o *ponto de virada*, ou seja, o menor nível de perda em que o HTTP/3 passa a ser mais rápido que o HTTP/2 de forma estatisticamente significativa.
- **Parte 2 (redes boas):** verificar se existe diferença entre os protocolos quando não há perda (0%).

## 2. Objetivo (template GQM de Basili)

| Elemento | Definição |
|---|---|
| **Analisar** | os protocolos HTTP/2 (sobre TCP + TLS 1.3) e HTTP/3 (sobre QUIC/UDP), servidos pelo Caddy e consumidos pelo Google Chrome |
| **com o propósito de** | comparar e avaliar |
| **com respeito a** | o desempenho de carregamento de página (tempo total de carga e TTFB) e a confiabilidade (taxa de falhas), sob diferentes níveis de perda de pacotes |
| **do ponto de vista de** | o usuário final que acessa a página e a equipe de operação que decide se vale a pena ativar o HTTP/3 |
| **no contexto de** | um ambiente controlado em Docker (um container servidor Caddy e um container cliente com Chrome), com rede degradada artificialmente por `tc netem` (0%, 1%, 2%, 3% e 5% de perda e atraso fixo) e uma página de teste com 30 a 50 recursos (imagens, CSS e scripts) |

**Em uma frase:** analisar os protocolos HTTP/2 e HTTP/3 com o propósito de compará-los com respeito ao tempo de carga, ao TTFB e à taxa de falhas, do ponto de vista do usuário final e da equipe de operação, no contexto de uma rede emulada com `tc netem` em ambiente Docker com Caddy e Chrome.

## 3. Perguntas (derivadas do objetivo)

| ID | Pergunta | Parte da pergunta de pesquisa |
|---|---|---|
| **Q1** | Em uma rede sem perda (0%), o tempo total de carga do HTTP/3 é diferente do HTTP/2? | Parte 2 |
| **Q2** | Em cada nível de perda (1%, 2%, 3%, 5%), o HTTP/3 carrega a página em menos tempo que o HTTP/2? | Parte 1 |
| **Q3** | A partir de qual nível de perda a vantagem do HTTP/3 passa a ser significativa, e qual o tamanho dessa vantagem? | Parte 1 (ponto de virada) |
| **Q4** | O tempo até o primeiro byte (TTFB) difere entre HTTP/2 e HTTP/3 em cada nível de perda? | Partes 1 e 2 |
| **Q5** | A proporção de cargas que falham difere entre HTTP/2 e HTTP/3 em cada nível de perda? | Partes 1 e 2 |

Q1 a Q3 respondem diretamente a pergunta de pesquisa. Q4 ajuda a explicar o resultado (o handshake do QUIC precisa de 1 RTT, contra 2 RTT do TCP + TLS 1.3). Q5 garante que um protocolo não pareça "mais rápido" apenas porque as cargas lentas dele falharam e saíram da amostra.

## 4. Métricas

### 4.1 Definição

| ID | Métrica | Como é calculada | Unidade |
|---|---|---|---|
| **M1** | Tempo total de carga | `loadEventEnd − startTime` da entrada de navegação (`performance.getEntriesByType('navigation')[0]`) | ms |
| **M2** | TTFB | `responseStart − startTime` da mesma entrada (inclui DNS, conexão e handshake, que é justamente onde os protocolos diferem) | ms |
| **M3** | Taxa de falhas | cargas que falharam ÷ cargas tentadas, por combinação (protocolo, perda). Uma carga **falha** quando: estoura o timeout definido no script, o Chrome retorna erro de navegação, ou o evento `load` não acontece | % |
| **M4** | Tamanho do efeito | Cliff's δ (ou Â₁₂ de Vargha-Delaney) entre HTTP/2 e HTTP/3 em cada nível de perda, para M1 e M2 | adimensional (−1 a 1) |
| **M5** | Diferença relativa das medianas | (mediana HTTP/2 − mediana HTTP/3) ÷ mediana HTTP/2 | % |
| **MC** | Protocolo efetivamente usado *(métrica de controle)* | `nextHopProtocol` da entrada de navegação (`h2` ou `h3`) | categórica |

**MC não responde nenhuma pergunta**: ela serve para validar os dados. Cargas em que o protocolo usado não é o esperado (ex.: pediu HTTP/3 e caiu para `h2`) são removidas e registradas na issue #12. A quantidade de fallbacks também é reportada, porque é uma informação útil por si só.

### 4.2 Rastreabilidade GQM

```
G: comparar HTTP/2 e HTTP/3 sob perda de pacotes
├── Q1 (0%: há diferença?)            → M1, M4, M5
├── Q2 (1–5%: HTTP/3 é mais rápido?)  → M1, M4, M5
├── Q3 (ponto de virada e tamanho)    → M1, M4, M5
├── Q4 (TTFB)                         → M2, M4
└── Q5 (falhas)                       → M3
    (validação de todas: MC)
```

### 4.3 Ligação com o CSV (issue #8)

| Coluna do CSV | Uso |
|---|---|
| `protocolo_pedido` | variável independente |
| `protocolo_usado` | MC |
| `perda_pct` | variável independente |
| `repeticao` | identificação da carga |
| `tempo_carga_ms` | M1 |
| `ttfb_ms` | M2 |
| `falhou` | M3 |

M4 e M5 são calculadas na análise (issues #13 e #14), não no CSV.

## 5. Variáveis

### 5.1 Variáveis independentes (fatores)

| Fator | Níveis | Como é controlado |
|---|---|---|
| **Protocolo** | HTTP/2, HTTP/3 | Flags do Chrome: `--disable-quic` para HTTP/2; `--enable-quic --origin-to-force-quic-on=<host>:443` para HTTP/3 (issue #6) |
| **Perda de pacotes** | 0%, 1%, 2%, 3%, 5% | `tc netem loss <p>%` na interface do container cliente (issue #7) |

O desenho é **fatorial completo 2 × 5 = 10 tratamentos**. O número de repetições por tratamento é definido na issue #9 (simulação de poder). A ordem das cargas deve ser **aleatorizada** (ou, no mínimo, alternada entre protocolos dentro de cada nível de perda) para que variações do host ao longo do tempo não se confundam com o efeito do protocolo.

### 5.2 Variáveis dependentes

| Variável | Métrica |
|---|---|
| Tempo total de carga | M1 |
| TTFB | M2 |
| Falha da carga (sim/não) | M3 |

### 5.3 Variáveis controladas (mantidas fixas)

| Variável | Valor |
|---|---|
| Atraso de rede | fixo em todos os tratamentos (valor definido na issue #7) |
| Página de teste | a mesma em todas as cargas, com 30 a 50 recursos (issue #5) |
| Versões do software | mesma versão do Caddy e do Chrome em toda a coleta (registradas no README) |
| Estado do navegador | perfil novo e cache vazio a cada carga, sem reaproveitar conexão nem retomada de sessão TLS (0-RTT), para que todo carregamento inclua o handshake completo |
| TLS | TLS 1.3 com certificado `tls internal` do Caddy nos dois protocolos |
| Hardware e host | mesma máquina, sem outras cargas pesadas rodando durante a coleta |

## 6. Hipóteses

### 6.1 Notação

- *T₂(p)* e *T₃(p)*: tempo total de carga (M1) com HTTP/2 e HTTP/3 no nível de perda *p*.
- *Md*: mediana. Usamos a mediana porque tempos de carga costumam ter distribuição assimétrica, com cauda longa à direita.
- Formalmente, como o teste sugerido é o de Mann-Whitney, as hipóteses comparam as distribuições: "HTTP/3 mais rápido" significa *P(T₃ < T₂) > 0,5*. Na escrita abaixo usamos a mediana para facilitar a leitura.

### 6.2 Hipóteses principais (M1, tempo total de carga)

**Nível 0% (redes boas, Q1): teste bilateral**, porque a pergunta é "existe diferença?" e não há expectativa forte de direção. O QUIC economiza 1 RTT no handshake, mas roda em espaço de usuário e pode gastar mais CPU.

| Perda | H0 | H1 |
|---|---|---|
| **0%** | *Md(T₃) = Md(T₂)*: não há diferença no tempo de carga entre HTTP/3 e HTTP/2 sem perda | *Md(T₃) ≠ Md(T₂)*: há diferença no tempo de carga entre HTTP/3 e HTTP/2 sem perda |

**Níveis 1% a 5% (redes ruins, Q2): teste unilateral**, porque a teoria prevê uma direção. No HTTP/2, todas as requisições compartilham uma única conexão TCP; um pacote perdido bloqueia todos os fluxos até ser retransmitido (*head-of-line blocking*). No HTTP/3, cada fluxo QUIC é independente, e a perda afeta só o fluxo do pacote perdido.

| Perda | H0 | H1 |
|---|---|---|
| **1%** | *Md(T₃) ≥ Md(T₂)*: com 1% de perda, o HTTP/3 não carrega a página mais rápido que o HTTP/2 | *Md(T₃) < Md(T₂)*: com 1% de perda, o HTTP/3 carrega a página mais rápido que o HTTP/2 |
| **2%** | *Md(T₃) ≥ Md(T₂)*: com 2% de perda, o HTTP/3 não carrega a página mais rápido que o HTTP/2 | *Md(T₃) < Md(T₂)*: com 2% de perda, o HTTP/3 carrega a página mais rápido que o HTTP/2 |
| **3%** | *Md(T₃) ≥ Md(T₂)*: com 3% de perda, o HTTP/3 não carrega a página mais rápido que o HTTP/2 | *Md(T₃) < Md(T₂)*: com 3% de perda, o HTTP/3 carrega a página mais rápido que o HTTP/2 |
| **5%** | *Md(T₃) ≥ Md(T₂)*: com 5% de perda, o HTTP/3 não carrega a página mais rápido que o HTTP/2 | *Md(T₃) < Md(T₂)*: com 5% de perda, o HTTP/3 carrega a página mais rápido que o HTTP/2 |

Mesmo com teste unilateral, a análise reporta o intervalo de confiança bilateral da diferença. Assim, se o HTTP/3 for **mais lento** em algum nível, isso aparece no resultado.

### 6.3 Ponto de virada (Q3)

Definição operacional, fixada antes da coleta:

> O **ponto de virada** *p\** é o menor nível de perda em que H0 é rejeitada **e** continua rejeitada em todos os níveis maiores.

Exemplos:

- Rejeita em 2%, 3% e 5%, mas não em 1% → *p\** = 2%.
- Rejeita em 1% e 5%, mas não em 2% e 3% → resultado não monotônico; *p\** = 5% e a inconsistência é discutida.
- Não rejeita em nenhum nível → "não foi encontrado ponto de virada entre 0% e 5%".

O tamanho do efeito (M4) é reportado em cada nível, para mostrar se a vantagem cresce com a perda.

### 6.4 Hipóteses secundárias

Seguem a mesma estrutura das principais, mas não definem o ponto de virada.

**TTFB (Q4, M2):** para cada *p* ∈ {0%, 1%, 2%, 3%, 5%}

- H0: *Md(TTFB₃(p)) = Md(TTFB₂(p))*
- H1: *Md(TTFB₃(p)) ≠ Md(TTFB₂(p))*

Teste bilateral em todos os níveis: o handshake do QUIC favorece o HTTP/3, mas o TTFB mede só a primeira resposta, então o efeito do *head-of-line blocking* tende a ser menor aqui do que no tempo total.

**Taxa de falhas (Q5, M3):** para cada *p* ∈ {0%, 1%, 2%, 3%, 5%}

- H0: *F₃(p) = F₂(p)*: a proporção de cargas que falham é igual nos dois protocolos
- H1: *F₃(p) ≠ F₂(p)*: a proporção de cargas que falham é diferente

### 6.5 Parâmetros dos testes (proposta; a confirmar na issue #9)

| Parâmetro | Proposta |
|---|---|
| Nível de significância | α = 0,05 |
| Teste para M1 e M2 | Mann-Whitney U (amostras independentes, sem supor normalidade) |
| Teste para M3 | Exato de Fisher (proporções com contagens pequenas) |
| Tamanho do efeito | Cliff's δ, com os limiares de Romano et al. (2006): \|δ\| < 0,147 desprezível; < 0,33 pequeno; < 0,474 médio; ≥ 0,474 grande |
| Comparações múltiplas | correção de Holm sobre os 5 testes de cada família (M1, M2, M3) |

**Observação sobre a Parte 2 (0%):** não rejeitar H0 em 0% **não prova** que os protocolos são iguais, só que não detectamos diferença. Se o grupo quiser afirmar que "em redes boas tanto faz", o caminho é um teste de equivalência (TOST) com uma margem definida **antes** da coleta (por exemplo, ±5% da mediana do HTTP/2). Essa decisão fica para a issue #9.
