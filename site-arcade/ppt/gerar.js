// Monta o PPTX do portfolio com a estetica do site: preto, vermelho e amarelo.
// A tipografia de marca (Oswald e Press Start 2P) entra como imagem, porque
// PowerPoint usa as fontes da maquina de quem abre e ninguem tem essas duas.
// O texto corrido continua sendo texto de verdade, editavel.
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const sizeOf = require('image-size');

const DADOS = JSON.parse(fs.readFileSync('conteudo.json', 'utf8'));
const IMG = p => path.join(__dirname, 'img', p);

const PRETO = '000000', BRANCO = 'FFFFFF', VERMELHO = 'FF2E35',
      AMARELO = 'FFD400', CINZA = '9C9CA4', CORPO = 'DCDCE0', GRAFITE = '1C1C1C';
const FONTE = 'Calibri';
const L = 13.333, A = 7.5, M = 0.62;          // largura, altura, margem
const SOB = 2.22;                             // primeira linha util sob o titulo gigante

// escala uma imagem pela largura (ou pela altura) mantendo a proporcao
function cx(arq, { w, h }) {
  const d = sizeOf.imageSize(fs.readFileSync(IMG(arq)));
  const r = d.width / d.height;
  return w ? { w, h: w / r } : { w: h * r, h };
}
function img(slide, arq, o) {
  const m = o.w ? cx(arq, { w: o.w }) : cx(arq, { h: o.h });
  const x = o.cx !== undefined ? o.cx - m.w / 2 : o.x;
  slide.addImage({ path: IMG(arq), x, y: o.y, w: m.w, h: m.h, ...(o.extra || {}) });
  return { ...m, x, y: o.y, fim: o.y + m.h };
}

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = 'Adilson Serafim Junior';
pres.title = 'Portfólio — Adilson Serafim Jr.';

function novo() {
  const s = pres.addSlide();
  s.background = { color: PRETO };
  return s;
}
const txt = (s, t, o) => s.addText(t, { isTextBox: true, fontFace: FONTE, margin: 0, ...o });

// estimativa de altura: Calibri tem largura media ~0,48 do corpo
function altura(texto, pt, w, entrelinha = 1.45) {
  const porLinha = Math.max(8, (w * 72) / (pt * 0.48));
  return Math.ceil(texto.length / porLinha) * pt * entrelinha / 72 + 0.06;
}

// bloco de destaque: filete vermelho + titulo + texto, o mesmo motivo do site
function destaque(s, titulo, corpo, { x, y, w }) {
  const hc = altura(corpo, 10, w - 0.16, 1.5);   // folga: a previa mede mais largo que o Calibri
  s.addShape(pres.ShapeType.rect, { x, y, w: 0.045, h: 0.3 + hc, fill: { color: VERMELHO } });
  txt(s, titulo.toUpperCase(), { x: x + 0.16, y, w: w - 0.16, h: 0.24,
    fontSize: 11, bold: true, color: BRANCO, charSpacing: 0.6 });
  txt(s, corpo, { x: x + 0.16, y: y + 0.28, w: w - 0.16, h: hc,
    fontSize: 10, color: CORPO, lineSpacing: 13.5, valign: 'top' });
  return y + 0.3 + hc;
}

// ---------------------------------------------------------------- 1. capa
{
  const s = novo();
  img(s, 'nome-topo.png', { x: M, y: 0.46, h: 0.17 });
  const ano = cx('ano.png', { h: 0.17 });
  img(s, 'ano.png', { x: L - M - ano.w, y: 0.46, h: 0.17 });

  const t = img(s, 't-portfolio.png', { cx: L / 2, y: 1.15, w: 7.7 });
  const my = t.y + t.h / 2;
  s.addShape(pres.ShapeType.line, { x: M, y: my, w: t.x - M - 0.45, h: 0,
    line: { color: '555555', width: 0.75 } });
  s.addShape(pres.ShapeType.line, { x: t.x + t.w + 0.45, y: my, w: L - M - (t.x + t.w + 0.45),
    h: 0, line: { color: '555555', width: 0.75 } });

  const fy = 3.85;
  img(s, DADOS.foto, { x: M, y: fy, w: 2.3, extra: { rounding: false } });
  const bx = M + 2.3 + 0.45;
  s.addShape(pres.ShapeType.rect, { x: bx, y: fy + 0.12, w: 6.55, h: 0.82,
    fill: { color: VERMELHO } });
  txt(s, 'ADILSON SERAFIM JR.', { x: bx + 0.2, y: fy + 0.12, w: 6.2, h: 0.82,
    fontSize: 33, bold: true, color: BRANCO, valign: 'middle', charSpacing: 0.4 });
  txt(s, 'Marketing de Influência & Community  |  Criador de Conteúdo',
    { x: bx, y: fy + 1.08, w: 6.55, h: 0.3, fontSize: 13, color: BRANCO });
  txt(s, DADOS.contato.local + '   ·   ' + DADOS.contato.email + '   ·   ' + DADOS.contato.tel,
    { x: bx, y: fy + 1.45, w: 6.55, h: 0.3, fontSize: 11.5, color: CINZA });
  img(s, DADOS.sprite, { x: L - M - 1.25, y: fy - 0.05, w: 1.25 });
  s.addNotes('Capa. Portfólio de Adilson Serafim Jr., 2026.');
}

// --------------------------------------------------------- 2. quem sou eu
{
  const s = novo();
  img(s, 'f-0.png', { x: M, y: M, h: 0.34 });
  img(s, 't-quem.png', { x: M, y: M + 0.52, h: 0.92 });
  img(s, DADOS.foto, { x: M, y: SOB + 0.15, w: 3.0 });
  const tx = M + 3.0 + 0.6, tw = L - M - tx;
  let y = SOB + 0.1;
  DADOS.perfil.forEach(p => {
    const limpo = p.replace(/<\/?strong>/g, '');
    const h = altura(limpo, 12.5, tw, 1.55);
    txt(s, limpo, { x: tx, y, w: tw, h, fontSize: 12.5, color: CORPO, lineSpacing: 19 });
    y += h + 0.2;
  });
  s.addNotes('Quem sou eu: trajetória e ponto de vista sobre comunidade e influência.');
}

// -------------------------------------------------------- 3. indice do work
{
  const s = novo();
  img(s, 'f-1.png', { x: M, y: M, h: 0.34 });
  img(s, 't-work.png', { x: M, y: M + 0.52, h: 0.92 });
  txt(s, 'Seis cases. Um por slide, com as competências antes da campanha.',
    { x: M, y: SOB, w: 9, h: 0.3, fontSize: 12.5, color: CINZA });
  let y = SOB + 0.62;
  DADOS.cases.forEach((c, i) => {
    // colunas fixas, para o cargo mais longo nao encostar no periodo
    const xCargo = 7.95, xPer = L - M - 1.8;
    txt(s, c.num, { x: M, y: y + 0.1, w: 1.1, h: 0.3, fontSize: 9.5, bold: true,
      color: VERMELHO, charSpacing: 0.8 });
    txt(s, c.empresa, { x: M + 1.2, y, w: xCargo - M - 1.3, h: 0.44, fontSize: 21,
      bold: true, color: BRANCO, charSpacing: 0.3 });
    txt(s, c.cargo, { x: xCargo, y: y + 0.1, w: xPer - xCargo - 0.12, h: 0.3,
      fontSize: 10.5, color: CINZA });
    txt(s, c.periodo, { x: xPer, y: y + 0.1, w: 1.8, h: 0.3, fontSize: 10.5,
      bold: true, color: VERMELHO, align: 'right' });
    y += 0.62;
    s.addShape(pres.ShapeType.line, { x: M, y: y - 0.1, w: L - 2 * M, h: 0,
      line: { color: GRAFITE, width: 0.75 } });
  });
  img(s, DADOS.sprite, { x: L - M - 0.95, y: A - 1.55, w: 0.95 });
  s.addNotes('Índice dos cases.');
}

// ----------------------------------------------------------- 4-9. os cases
const MIDIA = {
  0: { tipo: 'poster', arq: '02-zmes-leapmotor.jpg', legenda: 'Ativação no Salão do Automóvel' },
  1: { tipo: 'poster', arq: '03-zmes-tesouro-direto.jpg', legenda: 'Campanha “Posso ser direto?”, com Marta',
       segundo: '07-tesouro-direto-rende.jpg', legenda2: 'Conteúdo criado por mim' },
  2: { tipo: 'foto', legenda: 'Bienal do Livro Rio 2025 — estande do TikTok' },
  3: { tipo: 'yt', arq: 'yt-warner.png',
       url: 'https://youtu.be/yD-STBTMjO0?t=14369',
       legenda: 'Campeonato de MK11 · moderação da transmissão ao vivo' },
  4: { tipo: 'foto', legenda: 'Equipe de redes sociais na Black Friday' },
  5: { tipo: 'yt', arq: 'yt-brahma.png',
       url: 'https://www.youtube.com/playlist?list=PLXEscQRSPytlQAWU0IlBYWQ-SiNnGBAYR',
       legenda: 'O Próximo Nº 1 · playlist completa' },
};

DADOS.cases.forEach((c, i) => {
  const s = novo();
  const m = MIDIA[i];
  const COL = 5.55;                       // coluna da midia, a esquerda
  const tx = M + COL + 0.62, tw = L - M - tx;

  img(s, 'f-1.png', { x: M, y: 0.46, h: 0.28 });
  img(s, 'n-' + i + '.png', { x: tx, y: 0.46, h: 0.17 });
  const tit = img(s, 'c-' + i + '.png', { x: tx, y: 0.78, w: Math.min(tw, cx('c-' + i + '.png', { h: 0.52 }).w) });
  txt(s, c.cargo, { x: tx, y: tit.fim + 0.1, w: tw * 0.62, h: 0.26, fontSize: 12, color: CINZA });
  txt(s, c.periodo, { x: tx + tw * 0.62, y: tit.fim + 0.1, w: tw * 0.38, h: 0.26,
    fontSize: 12, bold: true, color: VERMELHO, align: 'right' });

  const chips = img(s, 'chips-' + i + '.png', { x: tx, y: tit.fim + 0.5, w: tw });
  const atuacao = c.atuacao.replace(/<\/?strong>/g, '');
  const ha = altura(atuacao, 11.5, tw, 1.48);
  txt(s, atuacao, { x: tx, y: chips.fim + 0.24, w: tw, h: ha,
    fontSize: 11.5, color: BRANCO, lineSpacing: 17 });
  if (c.destaque) {
    destaque(s, 'Destaque — ' + c.destaque[0].replace(/^Destaque — /, ''),
      c.destaque[1].replace(/<\/?strong>/g, ''),
      { x: tx, y: chips.fim + 0.34 + ha, w: tw });
  }

  // coluna da midia, centrada na vertical para nao sobrar um vazio embaixo
  const TOPO = 1.05, BASE = A - 0.55;
  const legAlt = 0.3, temLink = m.tipo === 'yt';
  const larg = m.segundo ? 3.62 : COL;
  const prev = cx(m.tipo === 'foto' ? c.fotos[0].arq : m.arq, { w: larg });
  const bloco = prev.h + legAlt + (temLink ? 0.36 : 0);
  let y = TOPO + Math.max(0, (BASE - TOPO - bloco) / 2);

  if (m.tipo === 'poster') {
    const p = img(s, m.arq, { x: M, y, w: larg });
    txt(s, m.legenda, { x: M, y: p.fim + 0.12, w: larg, h: legAlt,
      fontSize: 10, color: CINZA, italic: true });
    if (m.segundo) {
      const q = img(s, m.segundo, { x: M + larg + 0.26, y, h: p.h });
      txt(s, m.legenda2, { x: M + larg + 0.26, y: q.fim + 0.12, w: 1.6, h: 0.44,
        fontSize: 10, color: AMARELO, italic: true });
    }
  } else if (m.tipo === 'foto') {
    const f = img(s, c.fotos[0].arq, { x: M, y, w: larg });
    txt(s, m.legenda, { x: M, y: f.fim + 0.12, w: larg, h: legAlt,
      fontSize: 10, color: CINZA, italic: true });
  } else {
    const v = img(s, m.arq, { x: M, y, w: larg, extra: { hyperlink: { url: m.url } } });
    txt(s, m.legenda, { x: M, y: v.fim + 0.12, w: larg, h: legAlt,
      fontSize: 10, color: CINZA, italic: true });
    txt(s, [{ text: '▶  Assistir no YouTube', options: { hyperlink: { url: m.url } } }],
      { x: M, y: v.fim + 0.46, w: larg, h: 0.3, fontSize: 11.5, bold: true, color: VERMELHO });
  }
  if (c.sprite) img(s, c.sprite, { x: L - M - 0.8, y: A - 1.3, w: 0.8 });
  s.addNotes(c.empresa + ' — ' + c.cargo + ' (' + c.periodo + ').');
});

// ------------------------------------------------------------ 10. inventario
{
  const s = novo();
  img(s, 'f-2.png', { x: M, y: M, h: 0.34 });
  img(s, 't-inventario.png', { x: M, y: M + 0.52, h: 0.92 });

  const cw = (L - 2 * M - 0.76) / 3;
  const largura = t => Math.min(cw, 0.28 + t.length * 0.088);   // chip de 10,5pt, com folga

  let baixo = 0;
  DADOS.grupos.forEach((g, i) => {
    const x0 = M + i * (cw + 0.38);
    txt(s, g.titulo, { x: x0, y: SOB + 0.14, w: cw, h: 0.3, fontSize: 14, bold: true,
      color: BRANCO, charSpacing: 0.4 });
    img(s, 'niv-' + i + '.png', { x: x0, y: SOB + 0.5, h: 0.145 });
    let x = x0, y = SOB + 0.84;
    g.itens.forEach(it => {                       // quebra de linha dentro da coluna
      const w = largura(it);
      if (x + w > x0 + cw + 0.01) { x = x0; y += 0.4; }
      s.addShape(pres.ShapeType.rect, { x, y, w, h: 0.32, fill: { color: GRAFITE } });
      txt(s, it, { x: x + 0.12, y, w: w - 0.24, h: 0.32, fontSize: 10.5, color: CORPO,
        valign: 'middle' });
      x += w + 0.1;
    });
    baixo = Math.max(baixo, y + 0.32);
  });

  const ay = baixo + 0.42;
  txt(s, 'Atributos do personagem', { x: M, y: ay, w: 5, h: 0.3,
    fontSize: 13, bold: true, color: BRANCO, charSpacing: 0.4 });
  let x = M, y = ay + 0.4;
  DADOS.atributos.forEach((a, i) => {
    const w = 0.36 + a.length * 0.083;
    if (x + w > L - M) { x = M; y += 0.46; }
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.36, rectRadius: 0.18,
      fill: { color: PRETO }, line: { color: i % 2 ? BRANCO : VERMELHO, width: 0.75 } });
    txt(s, a, { x: x + 0.14, y, w: w - 0.28, h: 0.36, fontSize: 10.5, color: CORPO,
      valign: 'middle', align: 'center' });
    x += w + 0.14;
  });
  s.addNotes('Inventário: ferramentas por nível de domínio e atributos.');
}

// --------------------------------------------------------------- 11. marcas
{
  const s = novo();
  img(s, 'f-3.png', { x: M, y: M, h: 0.34 });
  img(s, 't-marcas.png', { x: M, y: M + 0.52, h: 0.92 });
  txt(s, 'Marcas atendidas em varejo, automotivo, entretenimento, finanças e causas.',
    { x: M, y: SOB, w: 10, h: 0.3, fontSize: 12.5, color: CINZA });
  const cols = 5, gw = (L - 2 * M - (cols - 1) * 0.22) / cols, gh = 1.2;
  DADOS.marcas.forEach((mc, i) => {
    const x = M + (i % cols) * (gw + 0.22), y = SOB + 0.5 + Math.floor(i / cols) * (gh + 0.2);
    s.addShape(pres.ShapeType.rect, { x, y, w: gw, h: gh,
      fill: { color: PRETO }, line: { color: GRAFITE, width: 1 } });
    const d = sizeOf.imageSize(fs.readFileSync(IMG(mc.arq)));
    const r = d.width / d.height;
    let w = gw - 0.5, h = w / r;
    if (h > gh - 0.5) { h = gh - 0.5; w = h * r; }
    s.addImage({ path: IMG(mc.arq), x: x + (gw - w) / 2, y: y + (gh - h) / 2, w, h });
  });
  s.addNotes('Marcas atendidas: ' + DADOS.marcas.map(m => m.nome).join(', ') + '.');
}

// --------------------------------------------------------------- 12. placar
{
  const s = novo();
  img(s, 'f-4.png', { x: M, y: M, h: 0.34 });
  img(s, 't-placar.png', { x: M, y: M + 0.52, h: 0.92 });
  const cw = (L - 2 * M - 4 * 0.34) / 5;
  DADOS.numeros.forEach(([v, rot], i) => {
    const x = M + i * (cw + 0.34);
    img(s, 'v-' + i + '.png', { x, y: SOB + 1.25, h: 1.05 });
    txt(s, rot, { x, y: SOB + 2.55, w: cw, h: 1.1, fontSize: 12, color: CINZA,
      lineSpacing: 16 });
  });
  s.addNotes('Placar: números reais, sem arredondar para cima.');
}

// -------------------------------------------------------------- 13. em cena
{
  const s = novo();
  img(s, 'f-5.png', { x: M, y: M, h: 0.34 });
  img(s, 't-cena.png', { x: M, y: M + 0.52, h: 0.92 });
  const intro = DADOS.cena_intro.replace(/<\/?strong>/g, '');
  txt(s, intro, { x: M, y: SOB, w: 11.6, h: altura(intro, 12.5, 11.6), fontSize: 12.5,
    color: CORPO });

  const cw = (L - 2 * M - 0.7) / 2, pw = 3.6, LINK_Y = 6.70;
  DADOS.cena.forEach((c, i) => {
    const x = M + i * (cw + 0.7);
    txt(s, c.titulo, { x, y: SOB + 0.58, w: cw, h: 0.34, fontSize: 15, bold: true,
      color: BRANCO });
    txt(s, c.meta, { x, y: SOB + 0.95, w: cw, h: 0.26, fontSize: 11, bold: true,
      color: VERMELHO });
    const p = img(s, path.basename(c.poster), { x, y: SOB + 1.26, w: pw });
    const corpo = c.texto.replace(/<\/?strong>/g, '');
    txt(s, corpo, { x, y: p.fim + 0.18, w: cw, h: LINK_Y - 0.12 - (p.fim + 0.18),
      fontSize: 9, color: CORPO, lineSpacing: 12 });
    // os dois links alinhados na mesma linha, independente do tamanho do texto
    txt(s, [{ text: c.materia + ' ↗', options: { hyperlink: { url: c.link } } }],
      { x, y: LINK_Y, w: cw, h: 0.28, fontSize: 11, bold: true, color: VERMELHO });
  });
  s.addNotes('Em cena: as duas campanhas nacionais em que atuei como elenco.');
}

// --------------------------------------------------------- 14. proxima missao
{
  const s = novo();
  img(s, 'f-6.png', { cx: L / 2, y: 0.95, h: 0.34 });
  img(s, 't-missao.png', { cx: L / 2, y: 1.48, h: 1.05 });
  img(s, DADOS.sprite, { cx: L / 2, y: 2.75, w: 1.35 });
  txt(s, DADOS.pitch.replace(/<\/?strong>/g, ''),
    { x: (L - 8) / 2, y: 4.5, w: 8, h: 0.62, fontSize: 13, color: CINZA,
      align: 'center', lineSpacing: 19 });

  const k = DADOS.contato;
  const itens = [
    ['E-MAIL', k.email, 'mailto:' + k.email],
    ['TELEFONE', k.tel, 'tel:' + k.tel_link],
    ['INSTAGRAM', k.insta, k.insta_link],
    ['LINKEDIN', 'in/adilson-serafim-junior', k.linkedin],
    ['PORTFÓLIO ONLINE', k.site.replace(/^https?:\/\//, '').replace(/\/$/, ''), k.site],
  ];
  // duas fileiras centradas: em uma so, o e-mail e o endereco do site estouram
  const larguras = itens.map(([, v]) => 0.5 + v.length * 0.092);
  const GAP = 0.2, MAXL = L - 2 * M;
  const fileiras = [[]];
  let usado = 0;
  itens.forEach((it, i) => {
    const w = larguras[i];
    if (usado + w > MAXL && fileiras[fileiras.length - 1].length) {
      fileiras.push([]); usado = 0;
    }
    fileiras[fileiras.length - 1].push(i);
    usado += w + GAP;
  });
  let fy2 = 5.36;
  fileiras.forEach(fil => {
    const larg = fil.reduce((a, i) => a + larguras[i], 0) + (fil.length - 1) * GAP;
    let x = (L - larg) / 2;
    fil.forEach(i => {
      const [rot, val, url] = itens[i], w = larguras[i];
      s.addShape(pres.ShapeType.rect, { x, y: fy2, w, h: 0.72,
        fill: { color: PRETO }, line: { color: '3A3A3A', width: 1 } });
      txt(s, rot, { x, y: fy2 + 0.1, w, h: 0.2, fontSize: 7.5, bold: true, color: VERMELHO,
        align: 'center', charSpacing: 0.7 });
      txt(s, [{ text: val, options: { hyperlink: { url } } }],
        { x, y: fy2 + 0.34, w, h: 0.28, fontSize: 12, bold: true, color: BRANCO,
          align: 'center' });
      x += w + GAP;
    });
    fy2 += 0.86;
  });
  img(s, 'local.png', { x: M, y: A - 0.62, h: 0.145 });
  const a = cx('assinatura.png', { h: 0.145 });
  img(s, 'assinatura.png', { x: L - M - a.w, y: A - 0.62, h: 0.145 });
  s.addNotes('Contato: ' + k.email + ' · ' + k.tel + ' · ' + k.site);
}

pres.writeFile({ fileName: process.argv[2] || 'portfolio-adilson-serafim.pptx' })
  .then(f => console.log('gerado:', f));
