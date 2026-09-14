# Área de teste

O portfólio tem **dois endereços**. Eles saem de duas branches diferentes deste
mesmo repositório, e uma nunca interfere na outra.

| | Branch | Para quê |
|---|---|---|
| **Oficial** | `claude/adilson-portfolio-onepage-ou5m9y` | O link que vai para as vagas. Só muda quando você aprovar. |
| **Teste** | `teste` | Rascunho. Pode quebrar à vontade. |

## O endereço de teste

```
https://adilsonserafim-git-teste-questha.vercel.app
```

Esse endereço é fixo. Toda vez que eu mandar algo para a branch `teste`, ele
atualiza sozinho — e o oficial fica parado.

O projeto na Vercel chama `adilsonserafim`, na conta `questha`. Por isso o
endereço de teste começa com `adilsonserafim` e não com `site-portf-lio`.

### Se pedir login para abrir

Na conta grátis o link de teste costuma ser público. Se aparecer uma tela da
Vercel pedindo login, é a proteção de preview:

**Settings → Deployment Protection → Vercel Authentication → Disabled**

## Como você reconhece qual é qual

O teste mostra um selo amarelo no canto superior direito: **VERSÃO DE TESTE**,
com o link do oficial ao lado. O oficial não mostra nada — o selo é ligado por
endereço, então ele some sozinho em produção.

Isso existe para uma coisa só: você nunca mandar o link errado para um
recrutador.

## O combinado

1. Toda experimentação vai para a `teste`.
2. Você abre o link de teste e diz se ficou bom.
3. Só depois do seu "pode ir" eu levo para o oficial.
4. Se não gostar, a `teste` é descartada e o oficial nem fica sabendo.
