#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o PDF do portfolio, para anexar em formulario de vaga.

Le o conteudo direto do index.html (o mesmo texto do site, sem nada
reescrito na mao) e monta um documento A4 claro, com texto de verdade —
selecionavel e legivel por sistema de recrutamento (ATS).

Uso:  python3 build-pdf.py [saida.pdf]
"""

import base64
import html as H
import io
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(AQUI, 'index.html')
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'portfolio-adilson-serafim.pdf')

CONTATO = {
    'email': 'aserafimjr@hotmail.com',
    'tel': '(11) 97599-9561',
    'tel_link': '+5511975999561',
    'insta': '@issoeadilson',
    'insta_link': 'https://www.instagram.com/issoeadilson',
    'linkedin': 'https://www.linkedin.com/in/adilson-serafim-junior-672799130/',
    'site': 'https://site-portf-lio-adilson.vercel.app/',
    'local': 'São Paulo · SP',
}


def preparar_logo(data_uri):
    """Deixa um logo da parede de marcas pronto para o fundo claro do PDF.

    Tres coisas acontecem aqui:

    1. GIF animado: o primeiro quadro costuma ser o inicio da animacao (no
       TikTok, uma tela preta). Os quadros seguintes sao deltas, entao eles
       sao compostos um sobre o outro ate formar a imagem cheia.
    2. Imagem sem transparencia: ela carrega o proprio fundo, quase sempre
       preto. A moldura desse fundo e aparada, senao o logo fica minusculo
       dentro de um quadrado.
    3. Escolha do ladrilho: a parede do site fica sobre preto, entao ha logos
       brancos e vazados, que sumiriam num fundo claro — esses ganham
       ladrilho escuro. Um logo escuro com fundo transparente precisa do
       contrario, ladrilho claro.

    Devolve (data URI, 'claro'|'escuro').
    """
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return data_uri, 'escuro'

    im = Image.open(io.BytesIO(base64.b64decode(data_uri.split(',', 1)[1])))

    if getattr(im, 'n_frames', 1) > 1:
        tela = Image.new('RGBA', im.size, (0, 0, 0, 0))
        for i in range(im.n_frames):
            im.seek(i)
            tela = Image.alpha_composite(tela, im.convert('RGBA'))
        im = tela
    else:
        im = im.convert('RGBA')

    px = list(im.getdata())
    opacos = [p for p in px if p[3] > 40]
    if not opacos:
        return data_uri, 'escuro'

    if len(opacos) / len(px) > 0.9:
        # imagem com fundo proprio: apara a moldura da cor do canto
        fundo = Image.new('RGBA', im.size, im.getpixel((0, 0)))
        caixa = ImageChops.difference(im, fundo).convert('L').point(lambda v: 255 if v > 18 else 0)
        if caixa.getbbox():
            im = im.crop(caixa.getbbox())
        tom = 'escuro'          # o proprio fundo do logo ja da o contraste
    else:
        lum = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in opacos) / len(opacos)
        tom = 'claro' if lum < 60 else 'escuro'

    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii'), tom


def curto(url):
    """Endereco sem o https:// e sem a barra final, para caber numa linha."""
    return re.sub(r'^https?://(www\.)?', '', url).rstrip('/')


def limpar(s):
    """Tira tags, normaliza espaco e devolve texto puro."""
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()


def negrito(s):
    """Mantem so o <strong> do site; o resto vira texto."""
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'<(?!/?strong\b)[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def ler_site():
    h = io.open(ENTRADA, encoding='utf-8').read()
    # os titulos do site tem o ponto final dentro de um <em> ("Work<em>.</em>");
    # tirar essas 6 tags deixa os titulos procuraveis como texto simples
    h = h.replace('<em>', '').replace('</em>', '')
    d = {}

    # --- perfil ("Quem sou eu?")
    bloco = h.split('Quem sou eu?')[1].split('<section id="work"')[0]
    d['perfil'] = [negrito(p) for p in re.findall(r'<p>(.*?)</p>', bloco, re.S)]
    m = re.search(r'<img class="foto" src="(data:image/[^"]+)"', h)
    d['foto'] = m.group(1) if m else ''

    # --- cases
    d['cases'] = []
    for item in h.split('<li class="work-item')[1:]:
        cab = re.search(r'<button class="work-cab".*?</button>', item, re.S).group(0)
        cab = re.sub(r'<span class="num">.*?</span>', '', cab, flags=re.S)
        cliente = re.search(r'<span class="cliente">(.*?)</span>', cab, re.S)
        c = {
            'empresa': limpar(re.sub(r'<span class="cliente">.*?</span>', '', cab, flags=re.S)),
            'cargo': limpar(cliente.group(1)) if cliente else '',
            'periodo': limpar(re.search(r'<p class="periodo">(.*?)</p>', item, re.S).group(1)),
            'competencias': [limpar(x) for x in re.findall(
                r'<li>(.*?)</li>', re.search(r'<ul class="competencias">(.*?)</ul>', item, re.S).group(1))],
            'atuacao': negrito(re.search(r'<p class="atuacao">(.*?)</p>', item, re.S).group(1)),
        }
        dest = re.search(r'<div class="destaque-bloco">\s*<h4>(.*?)</h4>\s*<p>(.*?)</p>', item, re.S)
        c['destaque'] = (limpar(dest.group(1)), negrito(dest.group(2))) if dest else None
        d['cases'].append(c)
    assert len(d['cases']) == 6, 'esperava 6 cases, achei %d' % len(d['cases'])

    # --- inventario (ferramentas por nivel + atributos)
    inv = h.split('Inventário.')[1].split('<section id="marcas"')[0]
    d['grupos'] = []
    for g in re.findall(r'<h3[^>]*>(.*?)</h3>.*?NÍVEL:\s*([^<]+)<.*?<ul[^>]*>(.*?)</ul>', inv, re.S):
        d['grupos'].append({'titulo': limpar(g[0]), 'nivel': limpar(g[1]),
                            'itens': [limpar(x) for x in re.findall(r'<li>(.*?)</li>', g[2])]})
    atr = re.search(r'Atributos do personagem.*?<ul[^>]*>(.*?)</ul>', inv, re.S)
    d['atributos'] = [limpar(x) for x in re.findall(r'<li>(.*?)</li>', atr.group(1))] if atr else []

    # --- marcas
    marcas = h.split('<div class="marcas-grade">')[1]
    d['marcas'] = re.findall(r'<img src="(data:image/[^"]+)"[^>]*alt="([^"]*)"', marcas)[:13]

    # --- numeros
    pl = h.split('Placar.')[1].split('<section id="cena"')[0]
    d['numeros'] = [(limpar(a), limpar(b)) for a, b in
                    re.findall(r'<div class="valor">(.*?)</div>\s*<p class="rotulo">(.*?)</p>',
                               pl, re.S)]
    assert len(d['numeros']) == 5, 'esperava 5 numeros, achei %d' % len(d['numeros'])

    # --- em cena
    cena = h.split('Em cena.')[1].split('<footer id="contato"')[0]
    d['cena_intro'] = negrito(re.search(r'<p class="intro-secao">(.*?)</p>', cena, re.S).group(1))
    d['cena'] = []
    for bloco in cena.split('<div class="cena-item">')[1:]:
        link = re.search(r'<a class="materia" href="([^"]+)"[^>]*>(.*?)</a>', bloco, re.S)
        d['cena'].append({
            'titulo': limpar(re.search(r'<h3>(.*?)</h3>', bloco, re.S).group(1)),
            'meta': limpar(re.search(r'<p class="quando">(.*?)</p>', bloco, re.S).group(1)),
            'texto': negrito(re.search(r'<p class="quando">.*?</p>\s*<p>(.*?)</p>',
                                       bloco, re.S).group(1)),
            'link': link.group(1),
            'materia': limpar(link.group(2)).rstrip(' \u2197'),
        })
    assert len(d['cena']) == 2, 'esperava 2 campanhas, achei %d' % len(d['cena'])

    # --- chamada final (o mesmo texto do rodape do site)
    d['pitch'] = negrito(re.search(r'<p class="pitch">(.*?)</p>', h, re.S).group(1))
    return d


# ----------------------------------------------------------------- documento
CSS = """
@page { size: A4; margin: 14mm 13mm 16mm 13mm; }
* { margin:0; padding:0; box-sizing:border-box }
:root { --tinta:#15161a; --suave:#5b6068; --linha:#e2e4e8; --acento:#d92b34; --fundo:#fff }
body { font-family:'Poppins',system-ui,sans-serif; color:var(--tinta); background:var(--fundo);
       font-size:9.2pt; line-height:1.5; -webkit-print-color-adjust:exact; print-color-adjust:exact }
h1,h2,h3,h4 { font-family:'Oswald',sans-serif; font-weight:700; line-height:1.12 }
a { color:var(--acento); text-decoration:none }

/* ---- cabecalho */
.topo { display:flex; gap:14px; align-items:center; border-bottom:2.5px solid var(--tinta);
        padding-bottom:10px; margin-bottom:14px }
.topo img { width:74px; height:74px; object-fit:cover; border:2px solid var(--tinta); flex:none }
.topo h1 { font-size:27pt; text-transform:uppercase; letter-spacing:-.01em }
.papel { font-family:'Oswald',sans-serif; font-weight:600; font-size:10.5pt;
         color:var(--acento); text-transform:uppercase; letter-spacing:.03em; margin-top:1px }
.contatos { margin-top:6px; font-size:8.3pt; color:var(--suave); line-height:1.65 }
.contatos b { color:var(--tinta); font-weight:600 }
.contatos a { color:var(--acento) } .contatos a b { color:var(--tinta) }

/* ---- secoes */
section { margin-top:13px; break-inside:auto }
h2 { font-size:12.5pt; text-transform:uppercase; letter-spacing:.05em;
     border-bottom:1.5px solid var(--linha); padding-bottom:3px; margin-bottom:8px }
h2 span { color:var(--acento) }
.perfil p { margin-bottom:5px; text-align:justify }

/* ---- experiencia */
.case { break-inside:auto; padding:9px 0 10px; border-bottom:1px solid var(--linha) }
.case-topo, .chips { break-inside:avoid; break-after:avoid }
.case:last-child { border-bottom:0 }
.case-topo { display:flex; justify-content:space-between; align-items:baseline; gap:10px }
.case h3 { font-size:12pt; text-transform:uppercase }
.case .cargo { font-family:'Oswald',sans-serif; font-weight:600; font-size:9.3pt; color:var(--acento);
               text-transform:uppercase; letter-spacing:.02em }
.case .periodo { font-size:8pt; color:var(--suave); white-space:nowrap; font-weight:500 }
.chips { display:flex; flex-wrap:wrap; gap:3px; margin:5px 0 6px; list-style:none }
.chips li { font-family:'Oswald',sans-serif; font-weight:500; font-size:7.6pt;
            text-transform:uppercase; letter-spacing:.03em; padding:1.5px 6px;
            border:1px solid var(--tinta); color:var(--tinta) }
.case p { text-align:justify }
.destaque { margin-top:5px; padding-left:8px; border-left:2.5px solid var(--acento);
             break-inside:avoid }
.destaque b { font-family:'Oswald',sans-serif; font-weight:600; font-size:8.6pt;
              text-transform:uppercase; letter-spacing:.02em; display:block; margin-bottom:1px }
.destaque p { font-size:8.7pt; color:#3c4046 }

/* ---- inventario */
.grade { display:grid; grid-template-columns:repeat(3,1fr); gap:9px }
.grupo { break-inside:avoid }
.grupo h4 { font-size:9.3pt; text-transform:uppercase }
.grupo .nivel { font-family:'Oswald',sans-serif; font-size:7.4pt; color:var(--acento);
                text-transform:uppercase; letter-spacing:.04em; margin-bottom:3px }
.grupo p { font-size:8.5pt; color:#3c4046 }
.atributos { margin-top:8px; font-size:8.5pt }
.atributos b { font-family:'Oswald',sans-serif; text-transform:uppercase; font-size:8.6pt }

/* ---- numeros */
.numeros { display:grid; grid-template-columns:repeat(5,1fr); gap:7px; break-inside:avoid }
.num { border-top:2.5px solid var(--acento); padding-top:4px }
.num b { font-family:'Oswald',sans-serif; font-weight:700; font-size:17pt; display:block; line-height:1 }
.num span { font-size:7.6pt; color:var(--suave); display:block; margin-top:2px; line-height:1.35 }

/* ---- marcas */
/* varios logos sao brancos ou vazados: num fundo claro sumiriam, entao cada um
   fica num ladrilho escuro, como na parede de marcas do site */
.logos { display:flex; flex-wrap:wrap; gap:5px; break-inside:avoid }
.logos span { display:inline-flex; align-items:center; justify-content:center;
              background:#15161a; padding:5px 9px; min-width:64px; height:30px }
.logos span.claro { background:#f0f1f3; border:1px solid var(--linha) }
.logos img { max-height:20px; max-width:82px; width:auto; height:auto }
.nota { font-size:7.8pt; color:var(--suave); margin-top:6px }

/* ---- em cena */
.cena { break-inside:avoid; margin-top:7px }
.cena h4 { font-size:9.8pt }
.cena .meta { font-size:7.8pt; color:var(--suave); margin-bottom:2px }
.cena p { font-size:8.7pt; text-align:justify }

/* ---- rodape */
.fim { margin-top:14px; border-top:2.5px solid var(--tinta); padding-top:8px; break-inside:avoid }
.fim p { font-size:9pt }
.fim .link { margin-top:5px; font-size:8.5pt; color:var(--suave) }
"""


def doc(d, fontes):
    e = H.escape

    def chips(xs):
        return '<ul class="chips">%s</ul>' % ''.join('<li>%s</li>' % e(x) for x in xs)

    cases = []
    for c in d['cases']:
        dest = ''
        if c['destaque']:
            dest = ('<div class="destaque"><b>%s</b><p>%s</p></div>'
                    % (e(c['destaque'][0]), c['destaque'][1]))
        cases.append(
            '<article class="case"><div class="case-topo"><div>'
            '<h3>%s</h3><div class="cargo">%s</div></div>'
            '<div class="periodo">%s</div></div>%s<p>%s</p>%s</article>'
            % (e(c['empresa']), e(c['cargo']), e(c['periodo']),
               chips(c['competencias']), c['atuacao'], dest))

    grupos = ''.join(
        '<div class="grupo"><h4>%s</h4><div class="nivel">%s</div><p>%s</p></div>'
        % (e(g['titulo']), e(g['nivel']), e(' · '.join(g['itens']))) for g in d['grupos'])

    numeros = ''.join('<div class="num"><b>%s</b><span>%s</span></div>' % (e(a), e(b))
                      for a, b in d['numeros'])

    marcas = [(preparar_logo(s), a) for s, a in d['marcas']]
    logos = ''.join('<span class="%s"><img src="%s" alt="%s"></span>' % (tom, uri, e(a))
                    for (uri, tom), a in marcas)

    cena = ''.join(
        '<div class="cena"><h4>%s</h4><div class="meta">%s</div><p>%s</p>'
        '<p><a href="%s">%s</a></p></div>'
        % (e(c['titulo']), e(c['meta']), c['texto'], e(c['link']), e(c['materia'])) for c in d['cena'])

    k = CONTATO
    return """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<title>Adilson Serafim Junior — Portfólio</title>
<style>%s</style><style>%s</style></head><body>

<header class="topo">
  <img src="%s" alt="Adilson Serafim Junior">
  <div>
    <h1>Adilson Serafim Jr.</h1>
    <div class="papel">Marketing de Influência &amp; Community · Criador de Conteúdo</div>
    <div class="contatos">
      %s &nbsp;·&nbsp; <a href="mailto:%s"><b>%s</b></a> &nbsp;·&nbsp; <a href="tel:%s"><b>%s</b></a> &nbsp;·&nbsp; <a href="%s">%s</a><br>
      LinkedIn: <a href="%s">%s</a> &nbsp;·&nbsp; Portfólio online: <a href="%s">%s</a>
    </div>
  </div>
</header>

<section class="perfil"><h2>Perfil</h2>%s</section>

<section><h2>Experiência <span>·</span> Cases</h2>%s</section>

<section><h2>Competências <span>&amp;</span> Ferramentas</h2>
  <div class="grade">%s</div>
  <p class="atributos"><b>Atributos:</b> %s</p>
</section>

<section><h2>Números</h2><div class="numeros">%s</div></section>

<section><h2>Marcas atendidas</h2><div class="logos">%s</div>
  <p class="nota">E outras marcas atendidas dentro de agência.</p></section>

<section><h2>Em cena</h2><p>%s</p>%s</section>

<footer class="fim">
  <p>%s</p>
  <p class="link">Portfólio completo, com os vídeos dos cases: <a href="%s">%s</a></p>
</footer>
</body></html>""" % (
        fontes, CSS, d['foto'],
        e(k['local']), e(k['email']), e(k['email']),
        e(k['tel_link']), e(k['tel']), e(k['insta_link']), e(k['insta']),
        e(k['linkedin']), e(curto(k['linkedin'])), e(k['site']), e(curto(k['site'])),
        ''.join('<p>%s</p>' % p for p in d['perfil']),
        ''.join(cases), grupos, e(' · '.join(d['atributos'])), numeros, logos,
        d['cena_intro'], cena, d['pitch'],
        e(k['site']), e(k['site']))


RENDER = r"""
const { chromium } = require('playwright');
(async () => {
  const [exe, entrada, saida] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage();
  await p.goto('file://' + entrada, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.pdf({ path: saida, format: 'A4', printBackground: true });
  await b.close();
})();
"""


def main():
    d = ler_site()
    print('lido do site: %d cases, %d grupos de ferramentas, %d números, %d marcas'
          % (len(d['cases']), len(d['grupos']), len(d['numeros']), len(d['marcas'])))

    # reaproveita o embutidor de fontes do build-offline, para o PDF sair com a
    # tipografia certa em qualquer maquina
    import importlib.util
    spec = importlib.util.spec_from_file_location('bo', os.path.join(AQUI, 'build-offline.py'))
    bo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bo)
    print('baixando fontes...')
    fontes = bo.css_das_fontes(
        'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700'
        '&family=Oswald:wght@500;600;700&display=swap')

    tmp = os.path.join(AQUI, '.portfolio-pdf.tmp.html')
    io.open(tmp, 'w', encoding='utf-8').write(doc(d, fontes))
    print('html intermediário: %.0f KB' % (os.path.getsize(tmp) / 1024))

    exe = next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
                            '/opt/pw-browsers/chromium/chrome-linux/chrome')
                if os.path.exists(c)), None)
    assert exe, 'chromium nao encontrado'
    # o script do renderizador precisa ficar ao lado do node_modules do playwright
    base = os.environ.get('PLAYWRIGHT_DIR', AQUI)
    js = os.path.join(base, 'render-pdf.js')
    io.open(js, 'w', encoding='utf-8').write(RENDER)
    env = dict(os.environ)
    env.pop('TMPDIR', None)   # o Chromium nao sobe com o perfil dentro do TMPDIR da sessao
    subprocess.run(['node', js, exe, tmp, SAIDA], check=True, env=env)
    os.remove(tmp)
    os.remove(js)
    print('\npronto: %s (%.1f MB)' % (os.path.basename(SAIDA),
                                      os.path.getsize(SAIDA) / 1024 / 1024))


if __name__ == '__main__':
    main()
