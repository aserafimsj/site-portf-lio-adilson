#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai do index.html tudo que o PPT precisa: textos e imagens.

Nada e reescrito na mao — o deck le o mesmo conteudo do site, entao os dois
nunca divergem. Grava conteudo.json e a pasta img/ ao lado deste arquivo.
"""
import base64, importlib.util, io, json, os, re, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
IMG = os.path.join(AQUI, 'img')


def carregar(nome):
    spec = importlib.util.spec_from_file_location(nome.replace('-', '_'),
                                                  os.path.join(SITE, nome + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    bp = carregar('build-pdf')
    d = bp.ler_site()
    shutil.rmtree(IMG, ignore_errors=True)
    os.makedirs(IMG)

    def salvar(uri, nome):
        cab, dados = uri.split(',', 1)
        ext = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif'}[cab.split(';')[0][5:]]
        caminho = os.path.join(IMG, nome + '.' + ext)
        open(caminho, 'wb').write(base64.b64decode(dados))
        return os.path.basename(caminho)

    saida = {k: d[k] for k in ('perfil', 'cases', 'grupos', 'atributos', 'numeros',
                               'cena', 'cena_intro', 'pitch', 'assinatura')}
    saida['contato'] = bp.CONTATO
    saida['foto'] = salvar(d['foto'], 'foto')
    saida['sprite'] = salvar(d['sprite'], 'sprite')
    saida['marcas'] = [{'nome': a, 'arq': salvar(bp.preparar_logo(s)[0], 'marca%02d' % i)}
                       for i, (s, a) in enumerate(d['marcas'])]

    h = io.open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
    h = h.replace('<em>', '').replace('</em>', '')
    work = h.split('<section id="work"')[1].split('<section id="inventario"')[0]
    itens = work.split('<li class="work-item')[1:]
    assert len(itens) == 6, 'esperava 6 cases, achei %d' % len(itens)

    for i, item in enumerate(itens):
        c = saida['cases'][i]
        c['posters'] = re.findall(r'poster="(posters/[^"]+)"', item)
        yt = re.search(r'data-yt="([^"]+)"', item)
        c['yt'] = yt.group(1) if yt else None
        # fotos reais do case (os spritezinhos sao tratados a parte)
        c['fotos'] = [{'arq': salvar(u, 'case%d-%d' % (i, j)), 'alt': bp.limpar(a)}
                      for j, (u, a) in enumerate(re.findall(
                          r'<img src="(data:image/jpe?g[^"]+)"[^>]*alt="([^"]*)"', item))]
        sp = re.search(r'<img class="sprite sprite-case" src="(data:image/png[^"]+)"', item)
        c['sprite'] = salvar(sp.group(1), 'spcase%d' % i) if sp else None

    cena = h.split('Em cena.')[1].split('<footer id="contato"')[0]
    for j, bloco in enumerate(cena.split('<div class="cena-item">')[1:]):
        saida['cena'][j]['poster'] = re.search(r'poster="(posters/[^"]+)"', bloco).group(1)

    for p in os.listdir(os.path.join(SITE, 'posters')):
        shutil.copy(os.path.join(SITE, 'posters', p), IMG)

    json.dump(saida, open(os.path.join(AQUI, 'conteudo.json'), 'w'),
              ensure_ascii=False, indent=1)
    print('conteudo: %d cases, %d marcas, %d imagens'
          % (len(saida['cases']), len(saida['marcas']), len(os.listdir(IMG))))


if __name__ == '__main__':
    main()
