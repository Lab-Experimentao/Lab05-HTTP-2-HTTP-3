# Página de teste

A página em [server/site/](../server/site/) é gerada por [scripts/gerar_pagina.py](../scripts/gerar_pagina.py) (`make pagina`). A seed é fixa (5), então rodar de novo produz os mesmos arquivos.

## Por que assim

- **Muitos recursos:** a multiplexação e o head-of-line blocking só fazem diferença entre HTTP/2 e HTTP/3 quando várias respostas disputam a mesma conexão.
- **Tamanhos variados:** de poucos KB a 200 KB em cada tipo, como numa página real.
- **Conteúdo aleatório:** não comprime, então o tamanho em disco é o que trafega. O Caddy também não está configurado com `encode`.
- **Tudo local:** nenhum recurso externo; tudo é servido pelo Caddy, na mesma origem.
- **Sem favicon:** `<link rel="icon" href="data:,">` impede o Chrome de pedir `/favicon.ico` por conta própria, o que somaria uma requisição fora do controle do experimento.
- **Carregamento:** CSS no `<head>`, JS com `defer` e imagens sem `loading="lazy"`, então o evento `load` só ocorre depois de todos os recursos.

## Resumo

| Tipo | Arquivos | Tamanho |
|---|---:|---:|
| html | 1 | 2,7 KB |
| imagem | 20 | 1.102,3 KB |
| css | 8 | 176,5 KB |
| js | 12 | 774,7 KB |
| **total** | **41** | **2.056,2 KB** |

São 40 recursos além do `index.html`.

## Arquivos

| Arquivo | Tamanho |
|---|---:|
| `index.html` | 2,7 KB |
| `img/imagem01.png` | 3,8 KB |
| `img/imagem02.png` | 6,1 KB |
| `img/imagem03.png` | 8,3 KB |
| `img/imagem04.png` | 9,8 KB |
| `img/imagem05.png` | 12,1 KB |
| `img/imagem06.png` | 15,1 KB |
| `img/imagem07.png` | 18,1 KB |
| `img/imagem08.png` | 21,8 KB |
| `img/imagem09.png` | 26,4 KB |
| `img/imagem10.png` | 30,1 KB |
| `img/imagem11.png` | 35,4 KB |
| `img/imagem12.png` | 39,9 KB |
| `img/imagem13.png` | 50,4 KB |
| `img/imagem14.png` | 60,1 KB |
| `img/imagem15.png` | 75,2 KB |
| `img/imagem16.png` | 90,2 KB |
| `img/imagem17.png` | 109,7 KB |
| `img/imagem18.png` | 130,0 KB |
| `img/imagem19.png` | 160,0 KB |
| `img/imagem20.png` | 199,8 KB |
| `css/estilo01.css` | 2,1 KB |
| `css/estilo02.css` | 4,0 KB |
| `css/estilo03.css` | 8,1 KB |
| `css/estilo04.css` | 12,1 KB |
| `css/estilo05.css` | 20,1 KB |
| `css/estilo06.css` | 30,0 KB |
| `css/estilo07.css` | 40,1 KB |
| `css/estilo08.css` | 60,1 KB |
| `js/script01.js` | 3,0 KB |
| `js/script02.js` | 6,1 KB |
| `js/script03.js` | 10,0 KB |
| `js/script04.js` | 15,0 KB |
| `js/script05.js` | 25,1 KB |
| `js/script06.js` | 35,0 KB |
| `js/script07.js` | 50,1 KB |
| `js/script08.js` | 70,1 KB |
| `js/script09.js` | 90,1 KB |
| `js/script10.js` | 120,0 KB |
| `js/script11.js` | 150,1 KB |
| `js/script12.js` | 200,1 KB |
