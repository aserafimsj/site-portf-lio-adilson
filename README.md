# Portfólio — Adilson Serafim Junior

Site one-page de **Adilson Serafim Junior**, Community Manager & Criador de Conteúdo (São Paulo/SP).
Estrutura de portfólio de agência: showreel em tela cheia, lista de cases em tipografia gigante,
parede de marcas, números e contato.

Preto e branco, um único acento (`#E63946`), muito espaço negativo. HTML, CSS e JavaScript puros —
sem framework, sem build, sem dependência além do Google Fonts.

## Rodar

Abra o `index.html` no navegador. É isso.

## Deploy

Arraste a pasta inteira para <https://app.netlify.com/drop>.

## Os dois sites deste repositório

| Pasta | Site | Deploy |
|---|---|---|
| raiz (`index.html`) | Portfólio one-page estilo agência | pendente |
| `site-arcade/` | Portfólio-jogo pixel ("Versão Arcade"), arquivo único e autossuficiente | Vercel — *Root Directory* apontando para `site-arcade` |

Na Vercel, cada site é um projeto separado apontando para uma pasta diferente deste mesmo
repositório. Todo push nesta branch republica o site sozinho.

## Estrutura

```
index.html        estrutura e conteúdo (todos os [SUBSTITUIR] estão aqui)
styles.css        estilos, do reset ao movimento reduzido
script.js         accordion, preview no cursor, contadores, lazy-load do YouTube
assets/videos/    showreel.mp4
assets/cases/     imagens dos cases
assets/logos/     logos das marcas
CHECKLIST.md      o que falta preencher e quais arquivos providenciar
```

## Antes de publicar

Leia o [CHECKLIST.md](CHECKLIST.md). Todo texto ou arquivo que ainda falta está marcado como
`[SUBSTITUIR]` no código, com um comentário em português explicando o que entra ali.
Nada no site é inventado — nenhum prêmio, número ou cliente que não seja real.

## Fontes

[Anton](https://fonts.google.com/specimen/Anton) nos títulos, [Inter](https://fonts.google.com/specimen/Inter)
no texto. Sem internet, o navegador cai para uma sans-serif do sistema e o layout continua de pé.
