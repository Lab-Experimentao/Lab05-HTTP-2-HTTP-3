"""Gera a página de teste (issue #5) em server/site/ e a tabela em docs/pagina.md.

Uso: python scripts/gerar_pagina.py

A seed é fixa: rodar de novo produz exatamente os mesmos arquivos.
O conteúdo é aleatório para não ser comprimível, então o tamanho em disco
é o tamanho transferido.
"""

import random
import struct
import zlib
from pathlib import Path

SEED = 5
RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "server" / "site"
DOC = RAIZ / "docs" / "pagina.md"

# Tamanhos alvo em KB, do menor ao maior em cada tipo (40 recursos no total).
TAMANHOS_KB = {
    "img": [4, 6, 8, 10, 12, 15, 18, 22, 26, 30, 35, 40, 50, 60, 75, 90, 110, 130, 160, 200],
    "css": [2, 4, 8, 12, 20, 30, 40, 60],
    "js": [3, 6, 10, 15, 25, 35, 50, 70, 90, 120, 150, 200],
}
LARGURA_IMG = 256  # px; a altura sai do tamanho alvo


def png(rng, tamanho):
    """PNG RGB com ruído, com tamanho próximo de `tamanho` bytes."""
    altura = max(1, round(tamanho / (LARGURA_IMG * 3 + 1)))
    linhas = b"".join(b"\x00" + rng.randbytes(LARGURA_IMG * 3) for _ in range(altura))

    def bloco(tipo, dados):
        crc = zlib.crc32(tipo + dados)
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", LARGURA_IMG, altura, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + bloco(b"IHDR", ihdr)
        + bloco(b"IDAT", zlib.compress(linhas, 0))
        + bloco(b"IEND", b"")
    ), altura


def css(rng, i, tamanho):
    partes = [f"/* estilo {i:02d} */\n"]
    n = 0
    while sum(map(len, partes)) < tamanho:
        cor = rng.randbytes(3).hex()
        dado = rng.randbytes(48).hex()
        partes.append(f'.e{i:02d}-{n} {{ color: #{cor}; --d: "{dado}"; }}\n')
        n += 1
    return "".join(partes).encode()


def js(rng, i, tamanho):
    inicio = f"/* script {i:02d} */\n(() => {{\n  const d = [\n"
    fim = "  ];\n  window.lab05 = (window.lab05 || 0) + 1;\n})();\n"
    partes = [inicio]
    while sum(map(len, partes)) + len(fim) < tamanho:
        partes.append(f'    "{rng.randbytes(48).hex()}",\n')
    partes.append(fim)
    return "".join(partes).encode()


def main():
    rng = random.Random(SEED)
    for pasta in ("img", "css", "js"):
        (SITE / pasta).mkdir(parents=True, exist_ok=True)
        for antigo in (SITE / pasta).iterdir():
            antigo.unlink()

    recursos = []  # (tipo, caminho, bytes)
    imgs = []
    for i, kb in enumerate(TAMANHOS_KB["img"], 1):
        dados, altura = png(rng, kb * 1024)
        caminho = f"img/imagem{i:02d}.png"
        (SITE / caminho).write_bytes(dados)
        recursos.append(("imagem", caminho, len(dados)))
        imgs.append((caminho, altura))
    for tipo, pasta, ext, gerar in (("css", "css", "css", css), ("js", "js", "js", js)):
        for i, kb in enumerate(TAMANHOS_KB[pasta], 1):
            dados = gerar(rng, i, kb * 1024)
            caminho = f"{pasta}/{'estilo' if ext == 'css' else 'script'}{i:02d}.{ext}"
            (SITE / caminho).write_bytes(dados)
            recursos.append((tipo, caminho, len(dados)))

    links = "\n".join(
        f'  <link rel="stylesheet" href="{c}">' for t, c, _ in recursos if t == "css"
    )
    scripts = "\n".join(
        f'  <script src="{c}" defer></script>' for t, c, _ in recursos if t == "js"
    )
    figuras = "\n".join(
        f'    <img src="{c}" width="{LARGURA_IMG}" height="{h}" alt="Imagem {i:02d}">'
        for i, (c, h) in enumerate(imgs, 1)
    )
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Lab05 - página de teste</title>
  <link rel="icon" href="data:,">
{links}
{scripts}
</head>
<body>
  <h1>Página de teste do Lab05</h1>
  <p>{len(recursos)} recursos locais: {len(imgs)} imagens, {len(TAMANHOS_KB['css'])} CSS e {len(TAMANHOS_KB['js'])} JS. Gerada por scripts/gerar_pagina.py.</p>
  <main>
{figuras}
  </main>
</body>
</html>
"""
    (SITE / "index.html").write_text(html, encoding="utf-8")
    recursos.insert(0, ("html", "index.html", len(html.encode())))

    escrever_doc(recursos)
    total = sum(b for *_, b in recursos)
    print(f"{len(recursos)} arquivos ({len(recursos) - 1} recursos + index.html), {kb_fmt(total)}")


def kb_fmt(b):
    return f"{b / 1024:,.1f} KB".replace(",", "X").replace(".", ",").replace("X", ".")


def escrever_doc(recursos):
    total = sum(b for *_, b in recursos)
    por_tipo = {}
    for t, _, b in recursos:
        n, s = por_tipo.get(t, (0, 0))
        por_tipo[t] = (n + 1, s + b)

    linhas = [
        "# Página de teste",
        "",
        "A página em [server/site/](../server/site/) é gerada por "
        "[scripts/gerar_pagina.py](../scripts/gerar_pagina.py) (`make pagina`). "
        f"A seed é fixa ({SEED}), então rodar de novo produz os mesmos arquivos.",
        "",
        "## Por que assim",
        "",
        "- **Muitos recursos:** a multiplexação e o head-of-line blocking só fazem diferença "
        "entre HTTP/2 e HTTP/3 quando várias respostas disputam a mesma conexão.",
        "- **Tamanhos variados:** de poucos KB a 200 KB em cada tipo, como numa página real.",
        "- **Conteúdo aleatório:** não comprime, então o tamanho em disco é o que trafega. "
        "O Caddy também não está configurado com `encode`.",
        "- **Tudo local:** nenhum recurso externo; tudo é servido pelo Caddy, na mesma origem.",
        "- **Sem favicon:** `<link rel=\"icon\" href=\"data:,\">` impede o Chrome de pedir "
        "`/favicon.ico` por conta própria, o que somaria uma requisição fora do controle "
        "do experimento.",
        "- **Carregamento:** CSS no `<head>`, JS com `defer` e imagens sem `loading=\"lazy\"`, "
        "então o evento `load` só ocorre depois de todos os recursos.",
        "",
        "## Resumo",
        "",
        "| Tipo | Arquivos | Tamanho |",
        "|---|---:|---:|",
    ]
    for t in ("html", "imagem", "css", "js"):
        n, s = por_tipo[t]
        linhas.append(f"| {t} | {n} | {kb_fmt(s)} |")
    linhas += [
        f"| **total** | **{len(recursos)}** | **{kb_fmt(total)}** |",
        "",
        f"São {len(recursos) - 1} recursos além do `index.html`.",
        "",
        "## Arquivos",
        "",
        "| Arquivo | Tamanho |",
        "|---|---:|",
    ]
    linhas += [f"| `{c}` | {kb_fmt(b)} |" for _, c, b in recursos]
    DOC.write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
