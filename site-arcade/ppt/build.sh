#!/bin/sh
# Gera o PPTX do portfolio do zero. Precisa de internet (baixa as fontes) e de
# node com pptxgenjs e image-size instalados nesta pasta.
set -e
cd "$(dirname "$0")"
python3 conteudo.py          # le o index.html: textos e imagens
python3 titulos.py           # tipografia de marca em PNG (Oswald, Press Start 2P)
python3 capas-yt.py          # capas dos dois videos que estao no YouTube
node gerar.js ../portfolio-adilson-serafim.pptx
python3 previa.py ../portfolio-adilson-serafim.pptx   # confere medidas e desenha previas
