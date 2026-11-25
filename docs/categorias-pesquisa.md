# Classificação da pesquisa (7 categorias)

> Issue #3 · Sprint 1 · Responsável: A (Planejamento e Método)
> **Primeira versão.** Será revisada na issue #17 para ficar coerente com o que foi de fato executado.

## Resumo

| # | Categoria | Classificação |
|---|---|---|
| 1 | Natureza | **Aplicada** |
| 2 | Abordagem | **Quantitativa** |
| 3 | Objetivo | **Explicativa** |
| 4 | Procedimento técnico | **Experimental** (experimento controlado) |
| 5 | Método científico | **Hipotético-dedutivo** |
| 6 | Ambiente | **Laboratório** (*in vitro*) |
| 7 | Horizonte temporal | **Transversal** |

## 1. Natureza: aplicada

**Justificativa:** o estudo não cria teoria nova sobre protocolos. Ele busca uma resposta prática para uma decisão concreta: se vale a pena ativar o HTTP/3 em servidores que atendem usuários em redes instáveis. Os objetos de estudo são softwares reais e em produção (Caddy e Chrome; ver [criterios-software.md](criterios-software.md)), e o resultado é traduzido em impacto com dados públicos (issue #16).

## 2. Abordagem: quantitativa

**Justificativa:** todas as variáveis dependentes são numéricas e coletadas automaticamente: tempo total de carga (ms), TTFB (ms) e taxa de falhas (%). As conclusões vêm de testes estatísticos e tamanho do efeito (Mann-Whitney, Cliff's δ), e não de interpretação de opiniões ou observações. Ver métricas M1–M5 em [gqm-hipoteses.md](gqm-hipoteses.md).

## 3. Objetivo: explicativa

**Justificativa:** o estudo não se limita a descrever como os protocolos se comportam. Ele testa uma relação de causa e efeito: se a **troca de protocolo** (HTTP/2 → HTTP/3) **causa** redução no tempo de carga sob perda de pacotes. As hipóteses partem de um mecanismo conhecido, o *head-of-line blocking* do TCP, que o QUIC elimina, e o experimento verifica se esse mecanismo produz efeito mensurável. Há também uma parte descritiva (estatística descritiva e boxplots, issue #13), mas ela serve para apoiar a explicação.

## 4. Procedimento técnico: experimental (experimento controlado)

**Justificativa:** os pesquisadores **manipulam deliberadamente** as variáveis independentes e medem o efeito nas dependentes, mantendo o resto fixo:

- **Fatores manipulados:** protocolo (2 níveis, via flags do Chrome) e perda de pacotes (5 níveis, via `tc netem`), num desenho fatorial completo 2 × 5.
- **Controle:** mesma página, mesmo atraso, mesmas versões de software, perfil do navegador novo a cada carga.
- **Aleatorização:** a ordem das cargas é sorteada ou alternada.
- **Repetição:** várias cargas por tratamento, com número definido por simulação de poder (issue #9).

Na classificação de Wohlin et al., é um **experimento orientado à tecnologia**: os tratamentos são aplicados a objetos (cargas de página) e não a participantes humanos. Por isso não há viés de sujeito nem necessidade de recrutar participantes.

## 5. Método científico: hipotético-dedutivo

**Justificativa:** o estudo parte de uma teoria (o QUIC evita o *head-of-line blocking* e tem handshake mais curto). Dela deduz hipóteses testáveis, com um par H0/H1 para cada nível de perda, escritas **antes** da coleta. Depois tenta refutá-las com dados. Se H0 não for rejeitada em algum nível, isso também é um resultado válido, e não um fracasso do estudo.

## 6. Ambiente: laboratório (*in vitro*)

**Justificativa:** a coleta acontece em um ambiente artificial e controlado: dois containers Docker na mesma máquina, com a rede degradada por `tc netem`. Isso dá controle total sobre a perda e o atraso e permite reproduzir o experimento. O custo é a **validade externa**: uma rede emulada não reproduz rajadas de perda, variação de banda, NATs e middleboxes que bloqueiam UDP numa rede móvel real. Esse limite será tratado nas ameaças à validade (issue #15) e na seção "o que não dá para afirmar" (issue #16).

## 7. Horizonte temporal: transversal

**Justificativa:** os dados são coletados num único período curto (menos de uma hora de coleta), com versões fixas do Caddy e do Chrome. O estudo compara os tratamentos entre si nesse momento e não acompanha como a diferença evolui ao longo do tempo ou entre versões dos softwares. Um estudo longitudinal exigiria repetir a coleta em várias versões, o que está fora do escopo.

---

## Reserva: categorias alternativas

Se a lista do enunciado tiver categorias diferentes das acima, seguem duas que também se aplicam:

| Categoria | Classificação | Justificativa curta |
|---|---|---|
| Fonte dos dados | **Primária** | Os dados são gerados pelo próprio experimento (CSV produzido pelo script Playwright, issue #8). Os dados secundários (W3Techs, StatCounter, Cloudflare) servem só para motivação e estimativa de impacto. |
| Grau de controle | **Controle total das variáveis** | Os dois fatores são definidos pelos pesquisadores via configuração (flags do Chrome e `tc netem`), e não observados como já existiam, como seria num quase-experimento ou estudo observacional. |
