# Área de teste

O portfólio tem **dois endereços**. Eles saem de duas branches diferentes deste
mesmo repositório, e uma nunca interfere na outra.

| | Branch | Para quê |
|---|---|---|
| **Oficial** | `claude/adilson-portfolio-onepage-ou5m9y` | O link que vai para as vagas. Só muda quando você aprovar. |
| **Teste** | `teste` | Rascunho. Pode quebrar à vontade. |

## O endereço de teste

A Vercel cria um endereço próprio para cada branch. O da branch `teste` tem
esta forma:

```
https://site-portf-lio-adilson-git-teste-<sua-conta>.vercel.app
```

O trecho `<sua-conta>` é gerado pela Vercel, então **você precisa copiar o
endereço uma vez** e me mandar, que eu anoto aqui:

1. Abra <https://vercel.com/dashboard> e entre no projeto.
2. Vá em **Deployments**.
3. Procure o deploy cuja branch é `teste`.
4. Clique nele e copie o endereço do topo.

Depois disso, o endereço é fixo: toda vez que eu mandar algo para a `teste`,
ele atualiza sozinho — e o oficial fica parado.

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
