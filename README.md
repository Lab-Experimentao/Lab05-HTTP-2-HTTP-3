# HTTP/3 vale a pena quando a internet está ruim? Um experimento com Caddy e Chrome

## O que é

O HTTP/3 é a versão mais nova do protocolo que os navegadores usam para carregar sites. Diferente do HTTP/2, ele funciona sobre o QUIC (UDP), e uma das promessas é lidar melhor com redes instáveis, em que pacotes se perdem no caminho, como no 4G fraco ou num Wi-Fi congestionado.

Este projeto testa essa promessa na prática. Usamos dois softwares reais e em produção: o servidor web Caddy, que já vem com HTTP/3 ativado, e o navegador Google Chrome. O Caddy é usado por 1,3% dos sites cujo servidor web é conhecido, o 7º mais usado segundo a [W3Techs](https://w3techs.com/technologies/details/ws-caddy), e tem cerca de 79,5 mil estrelas no [GitHub](https://github.com/caddyserver/caddy). O Chrome é o navegador mais usado no Brasil, com 79,1% de participação em todas as plataformas e 76,6% no celular ([StatCounter](https://gs.statcounter.com/browser-market-share/all/brazil), outubro de 2026). Já o HTTP/3 é suportado por 41,2% dos sites ([W3Techs](https://w3techs.com/technologies/details/ce-http3), novembro de 2026) e respondeu por 21% das requisições atendidas pela Cloudflare em 2025 ([Cloudflare Radar](https://blog.cloudflare.com/radar-2025-year-in-review/)). Fontes acessadas em 25/11/2026; detalhes em [docs/criterios-software.md](docs/criterios-software.md).

## Como executar

Requisitos: Docker com Compose e `make`.

| Comando | O que faz |
|---|---|
| `make up` | constrói e sobe os dois containers (servidor Caddy e cliente Chrome + Playwright) |
| `make test` | testa as portas e o Chrome em HTTP/2 e HTTP/3 |
| `make ps` / `make logs` | mostra o estado / os logs dos containers |
| `make client` / `make server` | abre um terminal no container |
| `make versions` | mostra as versões do Caddy e do Chrome |
| `make rede PERDA=2` | aplica a perda (0, 1, 2, 3 ou 5%) e o atraso fixo; ver [docs/rede.md](docs/rede.md) |
| `make rede-status` / `make rede-limpar` | mostra / remove as regras de rede |
| `make test-rede` | testa os 5 níveis de perda |
| `make down` | para e remove os containers |

Versões verificadas em 25/11/2026: Caddy 2.11.9, Google Chrome 158.0.8127.88 e Playwright 1.65.1.

### Como o protocolo é forçado

O cliente confia na CA local do Caddy (`client/start.sh`), e o Chrome é aberto com flags diferentes (`client/browser.js`):

| Protocolo | Flags |
|---|---|
| HTTP/2 | `--disable-quic` |
| HTTP/3 | `--enable-quic --origin-to-force-quic-on=caddy.test:443` |

O protocolo usado é conferido por `nextHopProtocol` e pelo DevTools (CDP). Sem forçar, o Chrome permaneceu em `h2` nos nossos testes, mesmo com o Caddy anunciando HTTP/3 via `alt-svc`.
