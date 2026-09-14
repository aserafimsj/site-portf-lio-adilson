#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera, como PNG, os pedacos do PPT que dependem das fontes do portfolio.

PowerPoint usa as fontes instaladas na maquina de quem abre o arquivo. Oswald
e Press Start 2P nao estao em praticamente nenhuma, e sem elas a identidade do
portfolio se perde. Entao tudo que e tipografia de marca — titulos gigantes,
etiquetas de fase, numeros vazados — vira imagem renderizada aqui, com as
fontes de verdade. O texto corrido do slide continua sendo texto de verdade.
"""
import base64, importlib.util, io, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
IMG = os.path.join(AQUI, 'img')
EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

spec = importlib.util.spec_from_file_location('bo', os.path.join(SITE, 'build-offline.py'))
bo = importlib.util.module_from_spec(spec); spec.loader.exec_module(bo)

PECAS = []


def peca(nome, html, extra=''):
    PECAS.append({'nome': nome, 'html': html, 'extra': extra})


def titulo(nome, txt, pont, cor='#fff', tam=120):
    peca(nome, '<span class="tit" style="font-size:%dpx;color:%s">%s<i>%s</i></span>'
               % (tam, cor, txt, pont))


def fase(nome, txt):
    peca(nome, '<span class="fase">%s</span>' % txt)


def pixel(nome, txt, cor='#ff2e35', tam=22):
    peca(nome, '<span class="px" style="font-size:%dpx;color:%s">%s</span>' % (tam, cor, txt))


def numero(nome, txt):
    peca(nome, '<span class="vazado">%s</span>' % txt)


def main():
    dados = json.load(open(os.path.join(AQUI, 'conteudo.json')))

    titulo('t-portfolio', 'Portfólio', '.', tam=190)
    titulo('t-quem', 'Quem sou eu', '?')
    titulo('t-work', 'Work', '.')
    titulo('t-inventario', 'Inventário', '.')
    titulo('t-marcas', 'Marcas', '.')
    titulo('t-placar', 'Placar', '.')
    titulo('t-cena', 'Em cena', '.')
    titulo('t-missao', 'Próxima missão', '!', tam=140)

    for i, f in enumerate(['FASE 0 · QUEM SOU EU', 'FASE 1 · WORK', 'FASE 2 · INVENTÁRIO',
                           'FASE 3 · MARCAS', 'FASE 4 · PLACAR', 'FASE 5 · EM CENA',
                           'FASE FINAL · PRÓXIMA MISSÃO']):
        fase('f-%d' % i, f)

    for i, c in enumerate(dados['cases']):
        peca('c-%d' % i, '<span class="tit" style="font-size:76px;color:#fff">%s</span>'
             % c['empresa'])
        pixel('n-%d' % i, c['num'])
        # os chips de competencia sao a assinatura visual do case: viram imagem
        # para sair identicos aos do site, com o Oswald de verdade
        peca('chips-%d' % i,
             '<ul class="chips">%s</ul>' % ''.join('<li>%s</li>' % x for x in c['competencias']),
             extra='style="width:760px"')

    for i, g in enumerate(dados['grupos']):
        pixel('niv-%d' % i, 'NÍVEL: ' + g['nivel'], tam=16)

    for i, (v, _) in enumerate(dados['numeros']):
        numero('v-%d' % i, v)

    pixel('assinatura', dados['assinatura'], cor='#9c9ca4', tam=16)
    pixel('local', dados['contato']['local'].upper(), cor='#9c9ca4', tam=16)
    pixel('nome-topo', 'ADILSON SERAFIM JUNIOR', cor='#fff', tam=18)
    pixel('ano', dados['contato'].get('ano', '2026'), cor='#fff', tam=18)

    fontes = bo.css_das_fontes(
        'https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
        '&family=Press+Start+2P&display=swap')

    corpo = ''.join(
        '<div class="peca" data-nome="%s" %s>%s</div>' % (p['nome'], p['extra'], p['html'])
        for p in PECAS)
    pagina = """<!DOCTYPE html><meta charset="UTF-8"><style>%s
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#000}
    .peca{display:inline-block;padding:6px 10px}
    .tit{font-family:'Oswald';font-weight:700;text-transform:uppercase;
         line-height:1;letter-spacing:.005em;white-space:nowrap;display:inline-block}
    .tit i{font-style:normal;color:#ff2e35}
    .fase{font-family:'Press Start 2P';font-size:18px;color:#fff;background:#ff2e35;
          padding:11px 14px;display:inline-block;box-shadow:6px 6px 0 rgba(255,255,255,.15);
          white-space:nowrap}
    .px{font-family:'Press Start 2P';white-space:nowrap;display:inline-block;line-height:1.5}
    .chips{list-style:none;display:flex;flex-wrap:wrap;gap:7px}
    .chips li{font-family:'Oswald';font-weight:600;font-size:19px;text-transform:uppercase;
              letter-spacing:.04em;color:#ffd400;border:1px solid rgba(255,212,0,.55);
              background:rgba(255,212,0,.09);padding:6px 10px;line-height:1}
    .vazado{font-family:'Oswald';font-weight:700;font-size:150px;line-height:.92;
            color:transparent;-webkit-text-stroke:5px #ff2e35;white-space:nowrap;
            display:inline-block}
    </style><body>%s</body>""" % (fontes, corpo)

    tmp = os.path.join(AQUI, '.titulos.html')
    io.open(tmp, 'w', encoding='utf-8').write(pagina)

    js = os.path.join(AQUI, '_shot.js')
    io.open(js, 'w', encoding='utf-8').write("""
const { chromium } = require('playwright');
(async () => {
  const [exe, pagina, destino] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage({ deviceScaleFactor: 3 });
  await p.goto('file://' + pagina);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  for (const el of await p.$$('.peca')) {
    const nome = await el.getAttribute('data-nome');
    await el.screenshot({ path: destino + '/' + nome + '.png', omitBackground: true });
  }
  await b.close();
})();
""")
    env = dict(os.environ); env.pop('TMPDIR', None)
    subprocess.run(['node', js, EXE, tmp, IMG], check=True, env=env)
    os.remove(tmp); os.remove(js)
    print('pecas geradas: %d' % len(PECAS))


if __name__ == '__main__':
    main()
