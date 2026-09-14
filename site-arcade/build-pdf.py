#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o PDF do portfolio, para anexar em formulario de vaga.

Le o conteudo direto do index.html (o mesmo texto do site, sem nada
reescrito na mao) e monta um A4 com a estetica do portfolio online: fundo
preto, vermelho e amarelo, fases em Press Start 2P, titulos gigantes em
Oswald e as competencias em chips amarelos antes da campanha.

O texto continua sendo texto de verdade, selecionavel e legivel por sistema
de recrutamento (ATS) — a estetica esta no fundo e na tipografia, nao numa
imagem de pagina.

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
        num = re.search(r'<span class="num">(.*?)</span>', cab, re.S)
        cliente = re.search(r'<span class="cliente">(.*?)</span>', cab, re.S)
        c = {
            'num': limpar(num.group(1)) if num else '',
            'empresa': limpar(re.sub(r'<span class="(?:cliente|num)">.*?</span>', '',
                                      cab, flags=re.S)),
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

    # --- ano do hero e o personagem em pixel, para o rodape
    ano = re.search(r'topinfo--ano"><span>(\d{4})</span>', h)
    CONTATO['ano'] = ano.group(1) if ano else ''
    ass = re.findall(r'<div class="assinatura">\s*<span>(.*?)</span>\s*<span>(.*?)</span>',
                     h, re.S)
    d['assinatura'] = limpar(ass[0][1]) if ass else ''
    with open(os.path.join(AQUI, 'sprites', 'parado', '00.png'), 'rb') as f:
        d['sprite'] = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')
    return d


# ----------------------------------------------------------------- documento
CSS = """
/* margem zero: so assim o preto cobre a folha inteira. O respiro de cima e de
   baixo vem do thead/tfoot da tabela abaixo, que o Chromium repete em toda
   pagina; as laterais vem do padding da celula. */
@page { size: A4; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box }

/* mesma paleta do site: preto, um vermelho e o amarelo do arcade */
:root {
  --preto:#000; --branco:#fff; --vermelho:#ff2e35; --amarelo:#ffd400;
  --corpo:#dcdce0; --cinza:#9c9ca4; --cinza-escuro:#1c1c1c;
  --linha:rgba(255,255,255,.22);
}
html, body { background:var(--preto) }
body { font-family:'Poppins',system-ui,sans-serif; color:var(--branco);
       font-size:8.8pt; line-height:1.62;
       -webkit-print-color-adjust:exact; print-color-adjust:exact }
h1,h2,h3,h4 { font-family:'Oswald',sans-serif; font-weight:700; line-height:1.08 }
a { color:var(--vermelho); text-decoration:none }
strong { font-weight:600 }

table.doc { width:100%; border-collapse:collapse; background:var(--preto) }
table.doc > thead td { height:11mm; padding:0 }
table.doc > tfoot td { height:11mm; padding:0 }
table.doc > tbody td { padding:0 11mm; vertical-align:top }

/* ---------- abertura ---------- */
.hero { border-bottom:3px solid var(--vermelho); padding-bottom:9px; margin-bottom:4px }
.hero-topo { display:flex; gap:13px; align-items:flex-end }
.hero img { width:76px; height:76px; object-fit:cover;
            border:2px solid var(--vermelho); flex:none }
.ano { font-family:'Press Start 2P'; font-size:6.4pt; color:var(--vermelho);
       display:block; margin-bottom:5px; letter-spacing:.02em }
.hero h1 { font-size:31pt; text-transform:uppercase; letter-spacing:-.005em; color:var(--branco) }
.hero h1 i { font-style:normal; color:var(--vermelho) }
.papel { font-family:'Oswald',sans-serif; font-weight:600; font-size:10pt;
         color:var(--amarelo); text-transform:uppercase; letter-spacing:.025em; margin-top:2px }

/* barra de contato no espirito do HUD */
.hud { margin-top:8px; border:1px solid var(--linha); background:#0b0b0b;
       padding:5px 8px; display:flex; flex-wrap:wrap; gap:4px 14px;
       font-size:7.9pt; color:var(--cinza); align-items:baseline }
.hud b { color:var(--branco); font-weight:600 }
.hud a { color:var(--branco) }
.hud .rot { font-family:'Press Start 2P'; font-size:5.4pt; color:var(--vermelho);
            letter-spacing:.02em; margin-right:2px }

/* ---------- secoes, no formato das fases do site ---------- */
section { margin-top:10px; break-inside:auto }
.step { display:inline-block; background:var(--vermelho); color:var(--branco);
        font-family:'Press Start 2P'; font-size:5.6pt; padding:.62em .8em;
        box-shadow:3px 3px 0 rgba(255,255,255,.15); margin-bottom:5px }
h2 { font-size:19pt; text-transform:uppercase; letter-spacing:.005em; margin-bottom:6px }
h2 i { font-style:normal; color:var(--vermelho) }
.perfil p { color:var(--corpo); margin-bottom:5px; text-align:justify }
.perfil strong { color:var(--branco) }

/* ---------- cases ---------- */
.case { padding:8px 0 9px; border-bottom:1px solid var(--cinza-escuro) }
.case:last-child { border-bottom:0 }
.case-topo { display:flex; align-items:baseline; gap:8px;
             break-inside:avoid; break-after:avoid }
.case .num { font-family:'Press Start 2P'; font-size:6pt; color:var(--vermelho);
             flex:none; letter-spacing:.02em }
.case h3 { font-size:14pt; text-transform:uppercase; color:var(--branco) }
.case .cliente { font-weight:500; font-size:7.8pt; color:var(--cinza);
                 margin-left:auto; white-space:nowrap }
.periodo { color:var(--vermelho); font-size:7.7pt; font-weight:600;
           margin:2px 0 4px; break-after:avoid }

/* as competencias vem antes da campanha, como no site */
.chips { display:flex; flex-wrap:wrap; gap:3px; margin-bottom:5px;
         list-style:none; break-inside:avoid; break-after:avoid }
.chips li { font-family:'Oswald',sans-serif; font-weight:600; font-size:7.1pt;
            text-transform:uppercase; letter-spacing:.04em; color:var(--amarelo);
            border:1px solid rgba(255,212,0,.55); background:rgba(255,212,0,.09);
            padding:1.6px 5.5px }
.atuacao { color:var(--branco); text-align:justify }
.atuacao strong { color:var(--amarelo) }
.destaque { margin-top:5px; padding-left:8px; border-left:3px solid var(--vermelho);
            break-inside:avoid }
.destaque b { font-family:'Oswald',sans-serif; font-weight:600; font-size:8.4pt;
              text-transform:uppercase; letter-spacing:.03em; color:var(--branco);
              display:block; margin-bottom:1px }
.destaque p { font-size:8.3pt; color:var(--corpo); text-align:justify }

/* ---------- inventario ---------- */
.grade { display:grid; grid-template-columns:repeat(3,1fr); gap:9px }
.grupo { break-inside:avoid }
.grupo h4 { font-size:9pt; text-transform:uppercase; color:var(--branco);
            letter-spacing:.03em }
.grupo .nivel { font-family:'Press Start 2P'; font-size:5.2pt; color:var(--vermelho);
                display:block; margin:2px 0 4px }
.grupo ul { display:flex; flex-wrap:wrap; gap:3px; list-style:none }
.grupo li { background:var(--cinza-escuro); color:var(--corpo);
            font-size:7.3pt; font-weight:500; padding:1.6px 5px }
.atributos { margin-top:9px; break-inside:avoid }
.atributos h4 { font-family:'Oswald',sans-serif; font-weight:600; font-size:8.6pt;
                text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px }
.pills { display:flex; flex-wrap:wrap; gap:4px; list-style:none }
.pills li { border:1px solid var(--branco); border-radius:999px; padding:1.6px 8px;
            font-size:7.4pt; font-weight:500; color:var(--corpo) }
.pills li:nth-child(odd) { border-color:var(--vermelho) }

/* ---------- placar ---------- */
.numeros { display:grid; grid-template-columns:repeat(5,1fr); gap:9px; break-inside:avoid }
.num-item b { font-family:'Oswald',sans-serif; font-weight:700; font-size:26pt;
              line-height:.95; display:block;
              color:transparent; -webkit-text-stroke:1.6px var(--vermelho) }
.num-item span { display:block; margin-top:3px; color:var(--cinza);
                 font-size:7.2pt; line-height:1.45 }

/* ---------- marcas: no preto elas funcionam como no site ---------- */
/* fileira incompleta nao pode virar um bloco cinza: o fio de separacao vem de
   um box-shadow em cada ladrilho, nao do fundo da grade */
.logos { display:grid; grid-template-columns:repeat(7,1fr); gap:1px;
         background:var(--preto); break-inside:avoid }
.logos span { background:var(--preto); height:34px;
              box-shadow:0 0 0 1px var(--cinza-escuro);
              display:flex; align-items:center; justify-content:center; padding:4px 6px }
.logos img { max-height:22px; max-width:100%; width:auto; height:auto }
.nota { font-size:7.4pt; color:var(--cinza); margin-top:5px }

/* ---------- em cena ---------- */
.cena { break-inside:avoid; margin-top:7px }
.cena h4 { font-size:9.6pt; color:var(--branco) }
.cena .meta { font-size:7.6pt; font-weight:600; color:var(--vermelho); margin:1px 0 3px }
.cena p { font-size:8.3pt; color:var(--corpo); text-align:justify }
.cena strong { color:var(--branco) }

/* ---------- tela de encerramento: uma pagina inteira, como a do site ---------- */
/* pagina inteira de encerramento: o miolo fica centrado e a assinatura desce
   para o pe da folha */
.fim { break-before:page; text-align:center; height:262mm;
       display:flex; flex-direction:column; align-items:center }
.fim-miolo { margin:auto 0 }
.fim .step { margin-bottom:9px; align-self:center }
.fim h2 { font-size:34pt; margin-bottom:8px }
.fim img { width:132px; height:auto; margin:14px auto 16px; display:block }
.fim .pitch { color:var(--cinza); max-width:56ch; margin:0 auto 18px; font-size:9.4pt }
.fim-contatos { display:flex; flex-wrap:wrap; gap:6px 10px; justify-content:center;
                list-style:none; margin-bottom:16px }
.fim-contatos li { border:1px solid var(--linha); padding:5px 11px }
.fim-contatos a, .fim-contatos span { color:var(--branco); font-weight:600; font-size:8.6pt }
.fim-contatos .rot { display:block; font-family:'Press Start 2P'; font-size:5pt;
                     color:var(--vermelho); margin-bottom:3px; font-weight:400 }
.assinatura { width:100%; padding-top:9px; border-top:1px solid var(--cinza-escuro);
              font-family:'Press Start 2P'; font-size:5.8pt; color:var(--cinza);
              display:flex; justify-content:space-between; gap:10px; line-height:1.9 }
"""


def doc(d, fontes):
    e = H.escape

    def titulo(txt, pont='.'):
        """Titulo gigante com a pontuacao em vermelho, como no site."""
        return '<h2>%s<i>%s</i></h2>' % (e(txt), pont)

    def fase(rotulo):
        return '<span class="step">%s</span>' % e(rotulo)

    cases = []
    for c in d['cases']:
        dest = ''
        if c['destaque']:
            dest = ('<div class="destaque"><b>%s</b><p>%s</p></div>'
                    % (e(c['destaque'][0]), c['destaque'][1]))
        cases.append(
            '<article class="case">'
            '<div class="case-topo"><span class="num">%s</span><h3>%s</h3>'
            '<span class="cliente">%s</span></div>'
            '<p class="periodo">%s</p>'
            '<ul class="chips">%s</ul>'
            '<p class="atuacao">%s</p>%s</article>'
            % (e(c['num']), e(c['empresa']), e(c['cargo']), e(c['periodo']),
               ''.join('<li>%s</li>' % e(x) for x in c['competencias']),
               c['atuacao'], dest))

    grupos = ''.join(
        '<div class="grupo"><h4>%s</h4><span class="nivel">NÍVEL: %s</span>'
        '<ul>%s</ul></div>'
        % (e(g['titulo']), e(g['nivel']), ''.join('<li>%s</li>' % e(i) for i in g['itens']))
        for g in d['grupos'])

    numeros = ''.join('<div class="num-item"><b>%s</b><span>%s</span></div>' % (e(a), e(b))
                      for a, b in d['numeros'])

    marcas = [(preparar_logo(s), a) for s, a in d['marcas']]
    logos = ''.join('<span><img src="%s" alt="%s"></span>' % (uri, e(a))
                    for (uri, _), a in marcas)

    cena = ''.join(
        '<div class="cena"><h4>%s</h4><p class="meta">%s</p><p>%s</p>'
        '<p><a href="%s">%s ↗</a></p></div>'
        % (e(c['titulo']), e(c['meta']), c['texto'], e(c['link']), e(c['materia']))
        for c in d['cena'])

    k = CONTATO
    return """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<title>Adilson Serafim Junior — Portfólio</title>
<style>%s</style><style>%s</style></head><body>
<table class="doc">
<thead><tr><td></td></tr></thead>
<tfoot><tr><td></td></tr></tfoot>
<tbody><tr><td>

<header class="hero">
  <div class="hero-topo">
    <img src="%s" alt="Adilson Serafim Junior">
    <div>
      <span class="ano">%s · PORTFÓLIO</span>
      <h1>Adilson Serafim Jr<i>.</i></h1>
      <div class="papel">Marketing de Influência &amp; Community · Criador de Conteúdo</div>
    </div>
  </div>
  <div class="hud">
    <span><span class="rot">LOCAL</span> %s</span>
    <span><span class="rot">E-MAIL</span> <a href="mailto:%s"><b>%s</b></a></span>
    <span><span class="rot">TEL</span> <a href="tel:%s"><b>%s</b></a></span>
    <span><span class="rot">INSTA</span> <a href="%s">%s</a></span>
    <span><span class="rot">IN</span> <a href="%s">%s</a></span>
    <span><span class="rot">SITE</span> <a href="%s">%s</a></span>
  </div>
</header>

<section class="perfil">%s%s%s</section>

<section>%s%s%s</section>

<section>%s%s
  <div class="grade">%s</div>
  <div class="atributos"><h4>Atributos do personagem</h4><ul class="pills">%s</ul></div>
</section>

<section>%s%s<div class="logos">%s</div>
  <p class="nota">E outras marcas atendidas dentro de agência.</p></section>

<section>%s%s<div class="numeros">%s</div></section>

<section>%s%s<p class="perfil">%s</p>%s</section>

<footer class="fim">
  <div class="fim-miolo">
  %s
  <h2>Próxima missão<i>!</i></h2>
  <img src="%s" alt="">
  <p class="pitch">%s</p>
  <ul class="fim-contatos">
    <li><span class="rot">E-MAIL</span><a href="mailto:%s">%s</a></li>
    <li><span class="rot">TELEFONE</span><a href="tel:%s">%s</a></li>
    <li><span class="rot">INSTAGRAM</span><a href="%s">%s</a></li>
    <li><span class="rot">LINKEDIN</span><a href="%s">%s</a></li>
    <li><span class="rot">PORTFÓLIO ONLINE</span><a href="%s">%s</a></li>
  </ul>
  </div>
  <div class="assinatura"><span>%s</span><span>%s</span></div>
</footer>
</td></tr></tbody></table>
</body></html>""" % (
        fontes, CSS, d['foto'], e(k['ano']),
        e(k['local']), e(k['email']), e(k['email']),
        e(k['tel_link']), e(k['tel']),
        e(k['insta_link']), e(k['insta']),
        e(k['linkedin']), 'LinkedIn',
        e(k['site']), e(curto(k['site'])),
        fase('FASE 0 · QUEM SOU EU'), titulo('Quem sou eu', '?'),
        ''.join('<p>%s</p>' % p for p in d['perfil']),
        fase('FASE 1 · WORK'), titulo('Work'), ''.join(cases),
        fase('FASE 2 · INVENTÁRIO'), titulo('Inventário'), grupos,
        ''.join('<li>%s</li>' % e(a) for a in d['atributos']),
        fase('FASE 3 · MARCAS'), titulo('Marcas'), logos,
        fase('FASE 4 · PLACAR'), titulo('Placar'), numeros,
        fase('FASE 5 · EM CENA'), titulo('Em cena'), d['cena_intro'], cena,
        fase('FASE FINAL · PRÓXIMA MISSÃO'), d['sprite'], d['pitch'],
        e(k['email']), e(k['email']),
        e(k['tel_link']), e(k['tel']),
        e(k['insta_link']), e(k['insta']),
        e(k['linkedin']), 'in/adilson-serafim-junior',
        e(k['site']), e(curto(k['site'])),
        e(k['local'].upper()), e(d['assinatura']))


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
