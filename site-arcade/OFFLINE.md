# Versões do portfólio para levar junto

São duas, para usos diferentes:

| Arquivo | Para quê | Peso |
|---|---|---|
| `portfolio-adilson-serafim.pdf` | **Anexar em formulário de vaga.** É o formato que os sites de candidatura aceitam. | ~370 KB |
| `portfolio-adilson-offline.html` | Apresentar o site completo, com os vídeos, sem internet. | ~40 MB |

---

# PDF para anexar

Gerado por `build-pdf.py`, que lê o conteúdo direto do `index.html` — nada é
reescrito à mão, então o PDF nunca diverge do site.

```bash
cd site-arcade
python3 build-pdf.py
```

Quatro páginas A4 **com a estética do site**: fundo preto, o vermelho e o
amarelo do arcade, as fases em Press Start 2P, títulos gigantes em Oswald,
competências em chips amarelos e o personagem em pixel na tela final. A ordem
é a mesma do online — Quem sou eu, Work, Inventário, Marcas, Placar, Em cena,
Próxima missão — e dentro de cada case as competências vêm antes da campanha.

O texto é de verdade, selecionável — cerca de 9.600 caracteres que um sistema
de triagem (ATS) consegue ler. A estética está no fundo e na tipografia, não
numa imagem de página.

Uma consequência do fundo preto: se alguém imprimir, gasta muita tinta. Para
tela — que é como quase todo recrutador abre — não muda nada. E-mail, telefone,
Instagram, LinkedIn, portfólio online e as duas matérias de imprensa são
links clicáveis.

Link de download, depois que a Vercel republicar:
<https://site-portf-lio-adilson.vercel.app/portfolio-adilson-serafim.pdf>

---

# Versão offline do site (arquivo único)

Um único arquivo `.html` que funciona **sem internet nenhuma**. Você abre com
dois cliques, direto do computador ou de um pen drive, e o site inteiro roda:
personagem, moedas, vídeos dos cases, fontes, tudo.

Serve para apresentar o portfólio numa entrevista sem depender do wi-fi do
lugar, ou para mandar para alguém que vai abrir depois.

## Como baixar

Abra o link abaixo e o navegador baixa o arquivo (não abre na tela — ele está
marcado para download):

<https://site-portf-lio-adilson.vercel.app/portfolio-adilson-offline.html>

Depois é só dar dois cliques no arquivo baixado. Funciona em qualquer
computador, com ou sem internet.

## Como gerar de novo

```bash
cd site-arcade
python3 build-offline.py
```

Sai um `portfolio-adilson-offline.html` de cerca de **40 MB** aqui na pasta.
O script precisa de internet só na hora de gerar (para baixar as fontes do
Google); o arquivo resultante não precisa de mais nada.

Gere de novo sempre que mudar o `index.html`, para a versão offline não ficar
para trás da versão publicada — e faça commit do arquivo gerado, porque é ele
que fica disponível no link de download acima.

## O que entra no arquivo

Tudo que hoje mora fora do HTML vira `data:` URI dentro dele:

| Item | Peso aproximado |
|---|---|
| 7 vídeos dos cases | 29 MB |
| 58 sprites do personagem | 250 KB |
| 7 capas de vídeo (posters) | 348 KB |
| Fontes Poppins, Oswald e Press Start 2P (subsets latin) | 300 KB |
| `moeda.png`, `favicon.png` | 46 KB |

O peso é quase todo vídeo — em especial o `07-tesouro-direto-rende.mp4`,
que sozinho é 19 MB dos 40.

## O que não dá para levar offline

Os **dois vídeos que estão no YouTube** (Warner/MK11 e VillaMix) não são
arquivos seus, então não podem ser embutidos. Nesses dois casos:

- a capa continua aparecendo, desenhada no estilo arcade do site;
- a legenda avisa: *"abre no YouTube (precisa de internet)"*;
- o clique abre o vídeo no navegador, em vez de tentar carregar um player
  que não funcionaria.

Os links de saída (LinkedIn, Instagram, B9, G1) também só abrem com internet.
São 4 links, e nenhum deles é necessário para a página se montar.

## Limites de tamanho, na prática

| Caminho | Passa? |
|---|---|
| Pen drive, HD externo | sim |
| Google Drive, WeTransfer, Dropbox | sim |
| WhatsApp Desktop (limite de 64 MB) | sim |
| Gmail como anexo (limite de 25 MB) | **não** — mande o link do Drive |
