#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desenha as capas dos dois videos que estao no YouTube.

As miniaturas oficiais ficam no i.ytimg.com, que esta bloqueado para download
aqui, e nao sao arquivos do Adilson. Entao entra uma capa no estilo arcade do
portfolio, com o titulo do video e o aviso de que o clique abre o YouTube.
"""
import importlib.util, io, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
spec = importlib.util.spec_from_file_location('bo', os.path.join(SITE, 'build-offline.py'))
bo = importlib.util.module_from_spec(spec); spec.loader.exec_module(bo)

CAPAS = [
    ('yt-warner', 'Liga Latina de<br>Mortal Kombat 11', 'MODERAÇÃO DA TRANSMISSÃO AO VIVO'),
    ('yt-brahma', 'O Próximo Nº 1', 'PLAYLIST COMPLETA DO REALITY'),
]

MOLDE = """<div class="capa" data-nome="%s">
  <div class="grade"></div>
  <div class="play"></div>
  <h3>%s</h3>
  <span class="aviso">%s</span>
  <span class="yt">▶ ASSISTA NO YOUTUBE</span>
</div>"""


def main():
    fontes = bo.css_das_fontes(
        'https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
        '&family=Press+Start+2P&display=swap')
    pagina = """<!DOCTYPE html><meta charset="UTF-8"><style>%s
*{margin:0;padding:0;box-sizing:border-box}
body{background:#111}
.capa{position:relative;width:640px;height:360px;overflow:hidden;
      background:radial-gradient(60%% 60%% at 50%% 42%%,#2b0d10,#080808);
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      border:2px solid rgba(255,46,53,.45);margin:8px}
.grade{position:absolute;inset:0;
       background-image:linear-gradient(#1b1b1b 1px,transparent 1px),
                        linear-gradient(90deg,#1b1b1b 1px,transparent 1px);
       background-size:18px 18px;opacity:.85}
.play{position:relative;width:74px;height:74px;background:#ff2e35;margin-bottom:20px}
.play::after{content:"";position:absolute;top:50%%;left:56%%;transform:translate(-50%%,-50%%);
             border-style:solid;border-width:15px 0 15px 25px;
             border-color:transparent transparent transparent #fff}
h3{position:relative;font-family:'Oswald';font-weight:700;font-size:38px;color:#fff;
   text-transform:uppercase;line-height:1.05;text-align:center;padding:0 28px}
.aviso{position:relative;font-family:'Oswald';font-weight:600;font-size:15px;color:#ffd400;
       letter-spacing:.08em;margin-top:10px;text-align:center;padding:0 28px}
.yt{position:absolute;bottom:0;left:0;right:0;font-family:'Press Start 2P';font-size:11px;
    color:#fff;background:rgba(255,46,53,.92);padding:10px;text-align:center}
</style><body>%s</body>""" % (fontes, ''.join(MOLDE % c for c in CAPAS))

    tmp = os.path.join(AQUI, '.capas.html')
    io.open(tmp, 'w', encoding='utf-8').write(pagina)
    js = os.path.join(AQUI, '_shot2.js')
    io.open(js, 'w', encoding='utf-8').write("""
const { chromium } = require('playwright');
(async () => {
  const [exe, pagina, destino] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage({ deviceScaleFactor: 3 });
  await p.goto('file://' + pagina);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  for (const el of await p.$$('.capa')) {
    await el.screenshot({ path: destino + '/' + await el.getAttribute('data-nome') + '.png' });
  }
  await b.close();
})();
""")
    env = dict(os.environ); env.pop('TMPDIR', None)
    subprocess.run(['node', js, EXE, tmp, os.path.join(AQUI, 'img')], check=True, env=env)
    os.remove(tmp); os.remove(js)
    print('capas: %d' % len(CAPAS))


if __name__ == '__main__':
    main()
