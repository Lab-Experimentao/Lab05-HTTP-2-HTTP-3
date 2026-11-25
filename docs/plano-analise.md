# Plano de análise

> Issue #9 · Definido **antes** da coleta. Perguntas, métricas e hipóteses: [gqm-hipoteses.md](gqm-hipoteses.md).

## Resumo

**Serão 90 cargas por combinação** (2 protocolos × 5 níveis de perda), ou **900 no total**.

| O que | Como |
|---|---|
| Tempo de carga e TTFB (M1, M2) | Mann-Whitney |
| Taxa de falhas (M3) | Exato de Fisher |
| Tamanho da diferença (M4, M5) | Cliff's δ e diferença das medianas |
| 5 níveis testados | correção de Holm, separada em M1, M2 e M3 |
| "Em rede boa tanto faz?" (0%) | teste de equivalência (TOST) em M1, margem de ±10% |

## Por que esses testes

- **Mann-Whitney, e não o t de Welch:** o t compara médias, e uma única carga muito lenta puxa a média. O Mann-Whitney compara a *ordem* dos tempos: quem costuma chegar na frente. O Welch não entra na conclusão, só confere se ela depende do teste.
- **Uma ou duas direções:** de 1 a 5% de perda, o tempo de carga pergunta "o HTTP/3 é *mais rápido*?" (unilateral). Em 0% e no TTFB, pergunta "há *diferença*?" (bilateral).
- **Exato de Fisher:** falhas devem ser poucas, e os testes aproximados erram com contagens pequenas.
- **Cliff's δ:** o p-valor diz se há diferença; o δ diz o tamanho. Vai de −1 a 1 e, neste projeto, é **positivo quando o HTTP/3 é mais rápido**.
- **Holm:** cada teste tem 5% de chance de alarme falso. Em 5 testes, a chance de ao menos um sobe para cerca de 23% (1 − 0,95⁵). Holm traz o total de volta a 5%, perdendo menos poder que Bonferroni [1].

## Por que esses números

| Número | Em palavras simples | Por que esse valor | Base |
|---|---|---|---|
| **α = 5%** | chance aceita de ver diferença onde não há | padrão da área, e o mesmo do Lab04 | convenção |
| **Poder = 80%** | chance de enxergar uma diferença que existe | com α = 5%, trata o alarme falso como 4 vezes mais grave que deixar passar (20% ÷ 5%); menos é arriscado, mais custa muitas cargas | Cohen [2] |
| **δ = 0,33** | menor efeito que queremos enxergar: em 100 pares de cargas, o HTTP/3 ganha cerca de 67 e perde 33 | é onde o efeito deixa de ser "pequeno" | limiares de Romano et al. [3] |
| **0,147 e 0,474** | fronteiras "desprezível/pequeno" e "médio/grande" (57 e 74 vitórias em 100) | rótulos para ler o resultado, não regras absolutas | [3] |
| **±10%** | se as medianas diferem menos que isso, dizemos "tanto faz" | **escolha do grupo**: metade dos 20% que se costuma citar como o mínimo perceptível em tempo de espera | regra prática, sem estudo primário localizado [4] |
| **IC de 90% no TOST** | faixa que precisa caber dentro de ±10% | são dois testes de 5%, um para cada lado | [5] |
| **IC de 95%** | faixa plausível da diferença das medianas | é o complemento de α = 5% | convenção |
| **α ÷ 5 = 1%** | limiar usado para dimensionar cada teste | é o primeiro e mais rígido passo de Holm com 5 níveis; quem passa nele passa nos demais | [1] |
| **10.000 simulações** | repetições do experimento no computador | a margem de erro do poder fica em ±1 ponto (1,96 × √(0,25 ÷ 10.000)) | cálculo |
| **1.000 simulações × 500 reamostras** | só no TOST, que é muito mais lento | margem de ±3 pontos, suficiente para a decisão | cálculo |
| **10.000 reamostras** | bootstrap da análise final | valor usual (1.000 a 10.000); usamos o maior porque roda uma só vez | [6] |
| **5% de falhas** | cenário pessimista da simulação | **suposição** nossa, por falta de piloto | a rever na #10 |
| **Semente 42** | torna o resultado repetível | arbitrária, a mesma do Lab04 | - |

## Por que 90 cargas

Simulamos o experimento milhares de vezes para cada tamanho de amostra, com [poder.py](../analise/poder.py), e contamos quantas vezes ele acerta. O critério foi: **o menor n, de 10 em 10, que chega a 80% em tudo abaixo.**

| Cargas por combinação | Bilateral, sem falhas | Bilateral, 5% de falhas | Unilateral, 5% de falhas | Acha o ponto de virada exato |
|---|---|---|---|---|
| 50 | 62% | 50% | 60% | 46% |
| 70 | 80% | 69% | 77% | 72% |
| 80 | 86% | 76% | 84% | 81% |
| **90** | **91%** | **81%** | **88%** | **87%** |
| 100 | 94% | 87% | 91% | 90% |

- **Efeito simulado:** δ = 0,33, com limiar de 1% nas três primeiras colunas de poder. Na última, o efeito começa em 2% de perda, fica constante, e os 5 testes passam por Holm.
- **O que define o n:** o teste bilateral com 5% de falhas, o caso mais difícil. Com 80 cargas ele fica em 76%.
- **Formato dos dados:** lognormal, cauda pesada e variâncias diferentes deram quase o mesmo poder (no máximo 0,5 ponto entre si, no n = 90 e δ = 0,33).
- **Alarmes falsos:** com Holm e sem efeito, ficaram entre 3,7% e 5,2%. Em testes isolados, chegaram a 5,6% no limiar de 5%, no pior caso.
- **Plano B, se não couber no tempo:** aceitar enxergar só efeitos grandes (δ = 0,474). Aí bastam **50** cargas (500 no total).

### Equivalência em 0%

Aqui o n depende de quanto os tempos variam (CV = desvio padrão ÷ média), que só o piloto vai mostrar. Com 90 cargas:

| CV | Chance de confirmar ±10% | Chance de confirmar ±5% |
|---|---|---|
| 5% | 100% | 100% |
| 10% | 100% | 69% |
| 15% | 95% | 14% |
| 20% | 71% | 1% |
| 30% | 16% | 0% |

Por isso a margem é ±10%, e não ±5%: com ±5%, 90 cargas só bastariam se os tempos variassem muito pouco. **Se o CV em 0% passar de cerca de 15%, a equivalência pode ficar inconclusiva**, e isso será dito no resultado. A tabela supõe medianas iguais, o caso mais favorável.

### Limite do teste de falhas

Com 90 cargas e o limiar de 1%, se um protocolo não falhar nenhuma vez, o outro precisa falhar ao menos **8** (8,9%) para o Fisher acusar diferença. Diferenças menores serão só descritas.

## Regras combinadas antes da coleta

1. **Carga que falhou** (timeout ou erro): entra como a *pior* no tempo de carga e no TTFB. Excluí-la favoreceria quem falha mais.
2. **Fallback** (pediu `h3` e veio `h2`): a carga é excluída, contada e refeita, para manter 90. Nos testes da #6 não houve nenhum.
3. **Outliers** não são removidos.
4. **Se a mediana cair numa carga que falhou** (metade ou mais falhas), não se reportam diferença de medianas nem IC, só δ e taxa de falhas.
5. **Ponto de virada:** definição da seção 6.3 do GQM, usando os p-valores após Holm de M1.
6. **O n não muda depois de ver os resultados.** Só pode ser revisto entre o piloto (#10) e a coleta (#11), pela variação e pelo tempo, nunca pelos p-valores. Os dados do piloto não entram na análise final.

## Limites deste plano

- O n usa distribuições **supostas**. O Mann-Whitney só usa a ordem dos valores, então a escala (ms ou s) não importa; a forma importa pouco, como visto acima.
- O piloto tem 5 cargas por combinação: serve para alertar sobre variação ou falhas muito altas, não para estimar o efeito.
- A simulação supõe cargas independentes. A ordem aleatória da #8 ajuda a sustentar isso.

## Como reproduzir

```
pip install -r analise/requirements.txt
make poder
```

Leva cerca de 5 minutos, confere as funções ([testar.py](../analise/testar.py)) e grava os CSVs em [analise/resultados](../analise/resultados).

**Do Lab04:** Mann-Whitney em lote, simulação Monte Carlo com semente por configuração e margem de erro. A calibração do Lab04 não se aplica, por ser de tempo de merge.

## Fontes

Acessadas em 25/11/2026, por busca e resumo das páginas. Onde indicado, a fonte é secundária.

1. Holm, S. (1979). *A Simple Sequentially Rejective Multiple Test Procedure*. Scandinavian Journal of Statistics 6(2), 65–70. [Registro](https://bibbase.org/network/publication/holm-asimplesequentiallyrejectivemultipletestprocedure-1979). Comparação com Bonferroni: [Wikipedia](https://en.wikipedia.org/wiki/Holm%E2%80%93Bonferroni_method) (secundária).
2. Cohen, J. (1992). *A Power Primer*. Psychological Bulletin 112(1), 155–159. [PubMed](https://pubmed.ncbi.nlm.nih.gov/19565683/).
3. Romano, J. et al. (2006), trabalho de congresso, citado na [documentação do pacote effsize](https://search.r-project.org/CRAN/refmans/effsize/html/cliff.delta.html) (secundária).
4. [Uptrends, *The psychology of web performance*](https://www.uptrends.com/blog/the-psychology-of-web-performance/) (blog). A ideia de que a percepção é relativa vem da [lei de Weber](https://en.wikipedia.org/wiki/Just-noticeable_difference).
5. Lakens, D. (2017). *Equivalence Tests: A Practical Primer*. [PMC5502906](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5502906/). Apresenta o TOST de Schuirmann (1987).
6. [Bootstrapping (Wikipedia)](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)) (secundária).
