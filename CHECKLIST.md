# CHECKLIST — antes do deploy

Portfólio one-page de **Adilson Serafim Junior** — Community Manager & Criador de Conteúdo, São Paulo/SP.

Nada neste site foi inventado. Todo campo abaixo está marcado com `[SUBSTITUIR]` no código e
precisa ser preenchido por você com informação real antes de publicar.

> **Como achar rápido no código:** busque por `[SUBSTITUIR` no `index.html`.
> Todos os pontos estão comentados em português logo acima da linha correspondente.

---

## 1. Assets que você precisa providenciar

### Vídeo

| Arquivo | Onde aparece | Especificação sugerida | OK? |
|---|---|---|---|
| `assets/videos/showreel.mp4` | Hero (tela cheia, autoplay, mudo, loop) | MP4 H.264, 1920×1080, até ~10 MB, 15–40 s, corte já pensado para tocar em loop | ☐ |

**Sem o arquivo o site não quebra:** o hero mostra fundo preto com o nome gigante (fallback)
e o botão de som some sozinho.

### Imagens dos cases (`assets/cases/`)

Formato sugerido: **.webp**, 1200×800 px (proporção 3:2), até ~200 KB cada.
Sem o arquivo aparece um placeholder cinza listrado com o nome do case.

| Arquivo | Case | OK? |
|---|---|---|
| `case_zmes.webp` | ZMES / Leapmotor | ☐ |
| `case_live.webp` | LIVE (ℓiⱴε) | ☐ |
| `case_innova.webp` | Innova / AATB | ☐ |
| `case_via_varejo.webp` | Via Varejo | ☐ |
| `case_warner_play.webp` | Warner Play / Execution | ☐ |
| `case_suzano.webp` | Suzano | ☐ |
| `case_mutato.webp` | Mutato | ☐ |
| `case_ref_mais.webp` | REF+ | ☐ |
| `case_grao_de_areia.webp` | Grão de Areia | ☐ |
| `case_isa.webp` | Instituto Socioambiental (ISA) | ☐ |

### Logos das marcas (`assets/logos/`)

Formato: **.png com fundo transparente** (ou SVG, se trocar a extensão no HTML).
Altura útil sugerida: 200–400 px. O CSS aplica preto e branco e revela a cor no hover.

| Arquivo | Marca | OK? |
|---|---|---|
| `logo_zmes.png` | ZMES / Leapmotor | ☐ |
| `logo_live.png` | LIVE | ☐ |
| `logo_innova.png` | Innova / AATB | ☐ |
| `logo_via_varejo.png` | Via Varejo | ☐ |
| `logo_warner_play.png` | Warner Play | ☐ |
| `logo_suzano.png` | Suzano | ☐ |
| `logo_mutato.png` | Mutato | ☐ |
| `logo_ref_mais.png` | REF+ | ☐ |
| `logo_grao_de_areia.png` | Grão de Areia | ☐ |
| `logo_isa.png` | Instituto Socioambiental | ☐ |
| *(extras)* | Duplique um `<li class="marcas__item">` no `index.html` para cada marca a mais | ☐ |

### Imagem de compartilhamento (opcional, mas recomendada)

| Arquivo | Onde aparece | Especificação | OK? |
|---|---|---|---|
| `assets/og.jpg` | Preview ao compartilhar o link (WhatsApp, LinkedIn) | 1200×630 px | ☐ |

---

## 2. Textos a substituir — `index.html`

### `<head>` (SEO / compartilhamento)

- [ ] `meta description` — descrição curta (até ~155 caracteres)
- [ ] `og:description` — mesma descrição
- [ ] `og:image` — confirmar se `assets/og.jpg` vai existir; se não, apagar as duas linhas de `og:image`

### Seção WORK — cargo e período (10 itens)

Cada item tem **um** `[SUBSTITUIR: cargo e período]` no botão. Ex.: `Community Manager · 2023–2024`.

- [ ] 01 — ZMES / Leapmotor
- [ ] 02 — LIVE (ℓiⱴε)
- [ ] 03 — Innova / AATB
- [ ] 04 — Via Varejo
- [ ] 05 — Warner Play / Execution
- [ ] 06 — Suzano
- [ ] 07 — Mutato
- [ ] 08 — REF+
- [ ] 09 — Grão de Areia
- [ ] 10 — Instituto Socioambiental (ISA)

### Seção WORK — descrição de 2–3 linhas (10 itens)

- [ ] 01 — ZMES / Leapmotor
- [ ] 02 — LIVE (ℓiⱴε)
- [ ] 03 — Innova / AATB
- [ ] 04 — Via Varejo
- [ ] 05 — Warner Play / Execution
- [ ] 06 — Suzano
- [ ] 07 — Mutato
- [ ] 08 — REF+
- [ ] 09 — Grão de Areia
- [ ] 10 — Instituto Socioambiental (ISA)

### Seção WORK — texto alternativo das imagens (`alt`) (10 itens)

Obrigatório para acessibilidade. Descreva o que a imagem mostra, não repita o nome da marca.

- [ ] 01 · [ ] 02 · [ ] 03 · [ ] 04 · [ ] 05 · [ ] 06 · [ ] 07 · [ ] 08 · [ ] 09 · [ ] 10

### Seção WORK — vídeos do YouTube (opcional, 10 espaços)

Cada case tem `<div class="work__video" data-youtube="[SUBSTITUIR: ID do vídeo do YouTube]">`.

- Para **ativar**: troque o valor pelo ID do vídeo (o trecho depois de `watch?v=`).
  Ex.: `data-youtube="dQw4w9WgXcQ"`. Aí aparece a thumbnail e o iframe só carrega no clique.
- Para **remover**: apague a `<div class="work__video" ...>` inteira daquele case.
- Enquanto ficar `[SUBSTITUIR]`, aparece uma caixa tracejada avisando que o espaço está reservado.

- [ ] Decidido case a case quais têm vídeo

### Seção MARCAS

- [ ] Conferir se os 10 nomes/logos estão certos
- [ ] Adicionar as marcas extras atendidas (duplicar o `<li>`) ou apagar os dois `<li class="marcas__item--vazio">` de exemplo

### Seção NÚMEROS

São 4 blocos. **A contagem animada só liga quando `data-valor` for um número de verdade** —
enquanto estiver `[SUBSTITUIR]`, o texto aparece discreto e nenhum número é inventado.

Para preencher, edite os dois atributos e o conteúdo:
`<span class="numeros__valor" data-valor="12" data-sufixo="+">12</span>`

- [ ] Nº 1 — `[X] comunidades geridas`
- [ ] Nº 2 — `[X]+ conteúdos publicados`
- [ ] Nº 3 — `[X] anos de experiência`
- [ ] Nº 4 — valor **e** rótulo (`[SUBSTITUIR: rótulo]`) — ou apagar o `<li>` inteiro se forem só 3 números

### Rodapé — contato

- [ ] E-mail — aparece **duas vezes** na mesma linha: no `href="mailto:..."` e no texto do link
- [ ] URL do LinkedIn
- [ ] URL do Instagram — ou apagar o `<li>` se não for usar
- [ ] URL do portfólio "Versão Arcade" (pixel art)
- [ ] URL do portfólio "Versão Jogo 3D"
- [ ] URL do "Adilsonline"

Já preenchido e conferido: `São Paulo / SP`, `Feito de verdade, sem case inventado.` e o ano
(atualiza sozinho via JavaScript).

---

## 3. Conferência final antes do deploy

- [ ] Buscar `[SUBSTITUIR` no projeto inteiro — não pode sobrar nenhum
- [ ] Abrir o `index.html` direto no navegador (duplo clique) e conferir tudo funcionando offline
- [ ] Testar no celular: os cases abrem no toque, nada estoura a largura da tela
- [ ] Testar navegação só pelo teclado (Tab / Enter) — os cases devem abrir e fechar
- [ ] Vídeo do hero: toca sozinho, mudo, em loop, e o botão de som liga/desliga
- [ ] Logos: preto e branco, ganham cor no hover (desktop)
- [ ] Números: contam ao entrar na tela
- [ ] Nenhum número, prêmio ou cliente que não seja real

## 4. Deploy (Netlify Drop)

1. Confirme que a pasta tem: `index.html`, `styles.css`, `script.js` e `assets/`.
2. Acesse <https://app.netlify.com/drop>.
3. Arraste a **pasta inteira** do projeto para a área indicada.
4. O site sobe com uma URL aleatória — dá para renomear em *Site settings → Change site name*
   ou apontar um domínio próprio.

Não há build, dependência ou variável de ambiente. A única coisa externa é o Google Fonts;
sem internet, o site cai para uma fonte sans-serif do sistema e continua funcionando.
