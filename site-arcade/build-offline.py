#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma versao OFFLINE do portfolio: um unico arquivo .html que funciona
sem internet nenhuma, aberto com dois cliques (file://).

Tudo que hoje e um arquivo separado ou um endereco da internet vira
data: URI dentro do proprio HTML:
  - fontes do Google (Poppins, Oswald, Press Start 2P), subsets latin
  - videos/*.mp4, posters/*.jpg, sprites/**/*.png, moeda.png, favicon.png
  - as duas capas de video hospedadas no i.ytimg.com

O que NAO da para levar offline: os dois videos que estao no YouTube
(Warner/MK11 e VillaMix). Nesses dois, a capa continua aparecendo e o
clique abre o YouTube no navegador — so funciona se houver internet.

Uso:  python3 build-offline.py [saida.html]
"""

import base64, io, os, re, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(AQUI, 'index.html')
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'portfolio-adilson-offline.html')

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
TIPOS = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
         '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon'}


def baixar(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def data_uri(dados, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(dados).decode('ascii'))


def embutir_arquivo(rel):
    caminho = os.path.join(AQUI, rel)
    mime = TIPOS.get(os.path.splitext(rel)[1].lower(), 'application/octet-stream')
    with open(caminho, 'rb') as f:
        return data_uri(f.read(), mime)


# ---------------------------------------------------------------- fontes
def css_das_fontes(url):
    """Baixa o CSS do Google Fonts e embute so os subsets latin/latin-ext."""
    css = baixar(url).decode('utf-8')
    saida, mantidos = [], 0
    # cada bloco vem precedido de um comentario com o nome do subset
    for bloco in re.split(r'(?=/\*)', css):
        m = re.match(r'/\*\s*([a-z0-9-]+)\s*\*/', bloco)
        if not m or m.group(1) not in ('latin', 'latin-ext'):
            continue
        u = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', bloco)
        if not u:
            continue
        bloco = bloco.replace(u.group(1), data_uri(baixar(u.group(1)), 'font/woff2'))
        saida.append(bloco.strip())
        mantidos += 1
    assert mantidos >= 8, 'poucas fontes embutidas: %d' % mantidos
    print('  fontes embutidas: %d arquivos woff2' % mantidos)
    return '\n'.join(saida)


# ------------------------------------------------- capa desenhada (sem YouTube)
CAPA_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
<defs>
<radialGradient id="f" cx="50%" cy="46%" r="62%">
<stop offset="0" stop-color="#2b0d10"/><stop offset="1" stop-color="#090909"/>
</radialGradient>
<pattern id="g" width="16" height="16" patternUnits="userSpaceOnUse">
<path d="M16 0H0v16" fill="none" stroke="#1c1c1c" stroke-width="1"/>
</pattern>
</defs>
<rect width="640" height="360" fill="url(#f)"/>
<rect width="640" height="360" fill="url(#g)"/>
<g fill="#ff2e35" opacity=".34">
<rect x="48" y="56" width="16" height="16"/><rect x="80" y="72" width="16" height="16"/>
<rect x="560" y="272" width="16" height="16"/><rect x="528" y="288" width="16" height="16"/>
<rect x="96" y="296" width="16" height="16"/><rect x="576" y="64" width="16" height="16"/>
</g>
<g fill="#ffd400" opacity=".22">
<rect x="64" y="288" width="16" height="16"/><rect x="544" y="56" width="16" height="16"/>
</g>
<rect x="8" y="8" width="624" height="344" fill="none" stroke="#ff2e35" stroke-width="3" opacity=".3"/>
</svg>"""


def capa_arcade():
    """Fundo arcade no lugar da miniatura do YouTube (o play e a legenda vem do CSS)."""
    return data_uri(CAPA_SVG.encode('utf-8'), 'image/svg+xml')


def main():
    h = io.open(ENTRADA, encoding='utf-8').read()
    print('lendo %s (%.0f KB)' % (os.path.basename(ENTRADA), len(h.encode()) / 1024))

    # 1) fontes: troca os <link> do Google por um <style> com tudo dentro
    m = re.search(r'<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*'
                  r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)"[^>]*>', h)
    assert m, 'nao achei os <link> das fontes'
    print('baixando fontes...')
    h = h[:m.start()] + '<style>\n' + css_das_fontes(m.group(1).replace('&amp;', '&')) + '\n</style>' + h[m.end():]

    # 2) capas do YouTube: as imagens moram no i.ytimg.com e nao podem ser
    #    embutidas, entao entra um fundo arcade desenhado aqui mesmo. O botao
    #    de play e a legenda ja sao desenhados por cima pelo CSS do site.
    capas = sorted(set(re.findall(r'https://i\.ytimg\.com/[^"]+', h)))
    assert capas, 'nao achei as capas do YouTube'
    for url in capas:
        print('desenhando capa arcade no lugar de %s' % url.split('/')[-2])
        h = h.replace(url, capa_arcade())

    # 3) arquivos locais referenciados direto no HTML/CSS
    locais = sorted(set(re.findall(r'(?:src|href|poster)="((?:videos|posters|sprites)/[^"]+)"', h)))
    locais += ['favicon.png', 'moeda.png']
    for rel in locais:
        print('embutindo %s (%.0f KB)' % (rel, os.path.getsize(os.path.join(AQUI, rel)) / 1024))
        uri = embutir_arquivo(rel)
        h = h.replace('"' + rel + '"', '"' + uri + '"')      # atributos HTML
        h = h.replace('url(' + rel + ')', 'url(' + uri + ')')  # url() do CSS

    # 4) sprites: o JS monta o caminho na mao, entao entra uma tabela de consulta
    acoes = dict(re.findall(r"(\w+):\s*\{n:(\d+)", h.split('var SPRITES = {')[1].split('};')[0]))
    tabela, total = [], 0
    for nome, n in sorted(acoes.items()):
        for i in range(int(n)):
            rel = 'sprites/%s/%02d.png' % (nome, i)
            total += os.path.getsize(os.path.join(AQUI, rel))
            tabela.append("'%s/%d':'%s'" % (nome, i, embutir_arquivo(rel)))
    print('embutindo %d sprites (%.0f KB)' % (len(tabela), total / 1024))

    antigo = ("    function caminho(nome, i){ return 'sprites/' + nome + '/' "
              "+ (i < 10 ? '0' : '') + i + '.png'; }")
    assert h.count(antigo) == 1, 'nao achei caminho()'
    h = h.replace(antigo,
        '    // versao offline: os sprites viram data: URI nesta tabela\n'
        '    var SPRITES_DATA = {' + ','.join(tabela) + '};\n'
        "    function caminho(nome, i){ return SPRITES_DATA[nome + '/' + i]; }")

    # 5) YouTube: sem internet o iframe nao carrega, entao o clique abre o site
    antigo_yt = "        var f = document.createElement('iframe');"
    assert h.count(antigo_yt) == 1, 'nao achei o carregador do YouTube'
    h = h.replace(
        "        var f = document.createElement('iframe');\n"
        "        f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?' + q.join('&');",
        "        // versao offline: abre no YouTube em vez de embutir o player\n"
        "        var w = 'https://www.youtube.com/watch?v=' + id;\n"
        "        if(caixa.dataset.inicio) w += '&t=' + caixa.dataset.inicio + 's';\n"
        "        if(caixa.dataset.lista) w += '&list=' + caixa.dataset.lista;\n"
        "        window.open(w, '_blank', 'noopener');\n"
        "        return;\n"
        "        var f = document.createElement('iframe');\n"
        "        f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?' + q.join('&');")
    # aviso honesto na legenda das duas capas
    h = re.sub(r'(<span class="yt-legenda">[^<]*)(</span>)',
               r'\1 · abre no YouTube (precisa de internet)\2', h)

    # 6) o compartilhamento aponta para o site publicado; offline nao ha URL
    h = h.replace('<title>', '<!-- VERSAO OFFLINE: arquivo unico, funciona sem internet -->\n<title>')

    io.open(SAIDA, 'w', encoding='utf-8').write(h)
    tam = os.path.getsize(SAIDA)
    print('\npronto: %s (%.1f MB)' % (os.path.basename(SAIDA), tam / 1024 / 1024))

    # conferencia: a pagina nao pode PEDIR nada da internet para se montar.
    # links em <a href> nao contam: sao navegacao, so abrem se a pessoa clicar.
    sem_ancoras = re.sub(r'<a\b[^>]*>', '', h)
    carrega = re.findall(r'(?:src|poster|href)="(https?://[^"]+)"', sem_ancoras)
    print('recursos externos que a pagina carregaria: %s' % (carrega or 'nenhum'))
    links = sorted(set(re.findall(r'<a\b[^>]*href="(https?://[^"]+)"', h)))
    print('links de saida (so abrem no clique, com internet): %d' % len(links))


if __name__ == '__main__':
    main()
