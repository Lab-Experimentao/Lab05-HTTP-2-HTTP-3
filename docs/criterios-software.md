# Critérios do software: Caddy, Chrome e adoção do HTTP/3

Objetivo: mostrar que os softwares do experimento são reais, relevantes e estão em produção, e que o HTTP/3 já é usado de verdade na web.

## 1. Caddy (servidor web)

| Indicador | Valor | Fonte | Período |
|---|---|---|---|
| Participação entre os servidores web dos sites | **1,3%** dos sites cujo servidor é conhecido (7º da lista, atrás de Cloudflare Server, Nginx, Apache, LiteSpeed, Node.js e Microsoft-IIS) | [W3Techs – Caddy](https://w3techs.com/technologies/details/ws-caddy) · [W3Techs – Web servers](https://w3techs.com/technologies/overview/web_server) | levantamento de 25/11/2026 |
| Estrelas no GitHub | **79.535** estrelas e 5.333 forks | [github.com/caddyserver/caddy](https://github.com/caddyserver/caddy) (API do GitHub) | 25/11/2026 |
| Manutenção ativa | última versão **v2.11.9**, publicada em 05/11/2026 | [Releases do Caddy](https://github.com/caddyserver/caddy/releases) | 25/11/2026 |

**Como ler:** 1,3% parece pouco, mas a W3Techs mede uma amostra dos sites mais visitados do mundo, o que equivale a dezenas de milhares de sites. Junto com as quase 80 mil estrelas e a release lançada no mês, isso mostra um software real, popular e mantido.

## 2. Google Chrome (navegador)

| Recorte | Chrome | 2º lugar | Fonte | Período |
|---|---|---|---|---|
| **Brasil, celular** | **76,56%** | Safari, 19,66% | [StatCounter – Mobile, Brasil](https://gs.statcounter.com/browser-market-share/mobile/brazil) | outubro/2026 |
| Brasil, todas as plataformas | **79,11%** | Safari, 7,68% | [StatCounter – Todas, Brasil](https://gs.statcounter.com/browser-market-share/all/brazil) | outubro/2026 |
| Mundo, todas as plataformas | **68,79%** | Safari, 16,59% | [StatCounter – Mundo](https://gs.statcounter.com/browser-market-share) | outubro/2026 |

**Como ler:** o Chrome é o navegador dominante, tanto no mundo quanto no Brasil e no celular brasileiro, que é o recorte que mais importa para a motivação do projeto.

## 3. Adoção do HTTP/3

| Indicador | Valor | Fonte | Período |
|---|---|---|---|
| Sites que suportam HTTP/3 | **41,2%** dos sites | [W3Techs – HTTP/3](https://w3techs.com/technologies/details/ce-http3) | novembro/2026 (acesso em 25/11/2026) |
| Requisições feitas via HTTP/3 (tráfego da Cloudflare, mundo) | **21%** das requisições (HTTP/2: 50%; HTTP/1.x: 29%) | [Cloudflare Radar 2025 Year in Review](https://blog.cloudflare.com/radar-2025-year-in-review/), seção "Adoption & usage" | 01/01 a 02/12/2025 |
| Sites que anunciam HTTP/3 via `alt-svc` *(complementar)* | cerca de **27%** dos sites | [Web Almanac 2024 – HTTP](https://almanac.httparchive.org/en/2024/http) | dados de 2024 |

**Como ler:** as duas métricas principais medem coisas diferentes e não se contradizem.

- **41,2% (W3Techs)** é a parcela de *sites* que oferecem HTTP/3.
- **21% (Cloudflare)** é a parcela de *requisições* que de fato trafegaram por HTTP/3.

A diferença existe porque nem todo cliente usa HTTP/3 mesmo quando o site oferece (por exemplo: a primeira visita costuma ir por HTTP/2, e algumas redes bloqueiam UDP). Para o texto base, os dois números juntos mostram que o HTTP/3 já está em produção em larga escala, mas ainda não é o padrão de fato.

## 4. Observações

- **Dados de 2026 da Cloudflare:** o Year in Review de 2026 costuma sair em dezembro. Se sair antes da entrega final, vale trocar o número de 2025 pelo de 2026 (issue #17).
- **Recorte Brasil para HTTP/3:** a página [radar.cloudflare.com/adoption-and-usage/br](https://radar.cloudflare.com/adoption-and-usage/br) tem esse dado, mas bloqueia acesso automatizado. Se o grupo quiser o número do Brasil, é preciso abrir no navegador e registrar valor e data manualmente.
- **Cuidado com a frase "muitos brasileiros acessam pelo celular":** no StatCounter, o celular aparece com só **34,67%** das visualizações de página no Brasil, contra 64,72% do desktop ([fonte](https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/brazil), outubro/2026). O StatCounter mede visualizações de página, e não pessoas. Por isso, a seção "Por que importa" deve se apoiar numa pesquisa de usuários, como a TIC Domicílios (Cetic.br), e não nesse número. Isso fica para a issue #16.

## 5. Trecho para o texto base

Substitui o marcador "[Inserir números de uso do Caddy, do Chrome e do HTTP/3, com fonte e data de acesso.]":

> O Caddy é usado por 1,3% dos sites cujo servidor web é conhecido, o 7º servidor mais usado segundo a W3Techs, e tem cerca de 79,5 mil estrelas no GitHub, com a versão mais recente (v2.11.9) lançada em novembro de 2026. O Chrome é o navegador mais usado no Brasil, com 79,1% de participação em todas as plataformas e 76,6% no celular (StatCounter, outubro de 2026). Já o HTTP/3 é suportado por 41,2% dos sites (W3Techs, novembro de 2026) e respondeu por 21% das requisições atendidas pela Cloudflare em 2025 (Cloudflare Radar). Fontes acessadas em 25/11/2026.
