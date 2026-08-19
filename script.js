/* =============================================================
   PORTFÓLIO — ADILSON SERAFIM JUNIOR
   JavaScript puro, sem dependências.
   ============================================================= */
(function () {
  'use strict';

  /* Preferência de movimento reduzido: desliga cursor, preview e contagem animada */
  var mqMovimento = window.matchMedia('(prefers-reduced-motion: reduce)');
  var movimentoReduzido = mqMovimento.matches;
  mqMovimento.addEventListener && mqMovimento.addEventListener('change', function (e) {
    movimentoReduzido = e.matches;
  });

  /* Só o desktop com mouse ganha hover, cursor customizado e preview */
  var temMouse = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ----------------------------------------------------------
     ANO DO RODAPÉ
     ---------------------------------------------------------- */
  var ano = document.getElementById('ano');
  if (ano) ano.textContent = String(new Date().getFullYear());

  /* ----------------------------------------------------------
     IMAGENS AUSENTES → mostra o placeholder cinza com o nome
     (enquanto os arquivos reais não forem colocados em /assets)
     ---------------------------------------------------------- */
  function marcarSemImagem(img) {
    var alvo = img.closest('.work__figura, .marcas__item, .work__preview');
    if (alvo) alvo.classList.add('sem-imagem');
  }
  function vigiarImagem(img) {
    img.addEventListener('error', function () { marcarSemImagem(img); });
    img.addEventListener('load', function () {
      var alvo = img.closest('.work__figura, .marcas__item, .work__preview');
      if (alvo) alvo.classList.remove('sem-imagem');
    });
    /* Caso a imagem já tenha falhado antes do script rodar */
    if (img.complete && img.naturalWidth === 0) marcarSemImagem(img);
  }
  Array.prototype.forEach.call(
    document.querySelectorAll('.work__figura img, .marcas__item img'),
    vigiarImagem
  );

  /* ----------------------------------------------------------
     MENU FIXO — fundo sólido ao rolar + link ativo por seção
     ---------------------------------------------------------- */
  var nav = document.getElementById('nav');
  function atualizarNav() {
    if (!nav) return;
    nav.classList.toggle('is-solido', window.scrollY > 40);
  }
  atualizarNav();
  window.addEventListener('scroll', atualizarNav, { passive: true });

  var linksNav = Array.prototype.slice.call(document.querySelectorAll('.nav__links a'));
  var secoesNav = linksNav
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  if ('IntersectionObserver' in window && secoesNav.length) {
    var obsNav = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        linksNav.forEach(function (a) {
          a.classList.toggle('is-ativo', a.getAttribute('href') === '#' + entrada.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    secoesNav.forEach(function (s) { obsNav.observe(s); });
  }

  /* ----------------------------------------------------------
     ANIMAÇÕES DE ENTRADA (fade + translate)
     ---------------------------------------------------------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !movimentoReduzido) {
    var obsReveal = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        entrada.target.classList.add('is-visivel');
        obs.unobserve(entrada.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    Array.prototype.forEach.call(reveals, function (el) { obsReveal.observe(el); });
  } else {
    Array.prototype.forEach.call(reveals, function (el) { el.classList.add('is-visivel'); });
  }

  /* ----------------------------------------------------------
     HERO — showreel e botão de som
     Se assets/videos/showreel.mp4 não existir, o vídeo some e
     fica só o fundo preto com o nome (fallback).
     ---------------------------------------------------------- */
  var hero = document.getElementById('hero');
  var video = document.getElementById('showreel');
  var botaoSom = document.getElementById('som');

  function semVideo() {
    if (hero) hero.classList.add('sem-video');
    if (botaoSom) botaoSom.hidden = true;
  }

  if (video) {
    var fonte = video.querySelector('source');
    if (fonte) fonte.addEventListener('error', semVideo);
    video.addEventListener('error', semVideo);
    /* NETWORK_NO_SOURCE = nenhum arquivo pôde ser carregado */
    video.addEventListener('loadedmetadata', function () {
      if (botaoSom) botaoSom.hidden = false;
    });
    window.setTimeout(function () {
      if (video.readyState === 0 && video.networkState === 3) semVideo();
    }, 1500);

    /* Autoplay mudo (exigência dos navegadores) */
    video.muted = true;
    var promessa = video.play();
    if (promessa && promessa.catch) promessa.catch(function () { /* silencioso */ });
  } else {
    semVideo();
  }

  if (botaoSom && video) {
    botaoSom.addEventListener('click', function () {
      var ligando = video.muted;
      video.muted = !ligando;
      botaoSom.setAttribute('aria-pressed', ligando ? 'true' : 'false');
      botaoSom.setAttribute('aria-label', ligando ? 'Desativar som do showreel' : 'Ativar som do showreel');
      if (ligando) {
        var p = video.play();
        if (p && p.catch) p.catch(function () {});
      }
    });
  }

  /* ----------------------------------------------------------
     WORK — accordion (funciona no mouse e no toque)
     ---------------------------------------------------------- */
  var botoesWork = Array.prototype.slice.call(document.querySelectorAll('.work__botao'));

  function fechar(botao) {
    var painel = document.getElementById(botao.getAttribute('aria-controls'));
    if (!painel || painel.hidden) return;
    botao.setAttribute('aria-expanded', 'false');
    painel.style.height = painel.scrollHeight + 'px';
    /* força reflow para a transição acontecer */
    void painel.offsetHeight;
    painel.style.height = '0px';
    var fim = function () {
      painel.hidden = true;
      painel.removeEventListener('transitionend', fim);
    };
    painel.addEventListener('transitionend', fim);
    window.setTimeout(fim, 600);
  }

  function abrir(botao) {
    var painel = document.getElementById(botao.getAttribute('aria-controls'));
    if (!painel) return;
    botao.setAttribute('aria-expanded', 'true');
    painel.hidden = false;
    var interno = painel.firstElementChild;
    painel.style.height = '0px';
    void painel.offsetHeight;
    painel.style.height = (interno ? interno.offsetHeight : painel.scrollHeight) + 'px';
    var fim = function () {
      painel.style.height = 'auto';
      painel.removeEventListener('transitionend', fim);
    };
    painel.addEventListener('transitionend', fim);
    window.setTimeout(fim, 600);
  }

  botoesWork.forEach(function (botao) {
    botao.addEventListener('click', function () {
      var aberto = botao.getAttribute('aria-expanded') === 'true';
      /* Um case aberto por vez — estilo lista de agência */
      botoesWork.forEach(function (outro) {
        if (outro !== botao && outro.getAttribute('aria-expanded') === 'true') fechar(outro);
      });
      if (aberto) { fechar(botao); } else { abrir(botao); esconderPreview(); }
    });
  });

  /* Recalcula a altura do painel aberto quando a tela muda de tamanho */
  window.addEventListener('resize', function () {
    botoesWork.forEach(function (botao) {
      if (botao.getAttribute('aria-expanded') !== 'true') return;
      var painel = document.getElementById(botao.getAttribute('aria-controls'));
      if (painel) painel.style.height = 'auto';
    });
  });

  /* ----------------------------------------------------------
     WORK — preview seguindo o cursor (apenas desktop)
     ---------------------------------------------------------- */
  var preview = document.getElementById('work-preview');
  var previewImg = preview ? preview.querySelector('img') : null;
  var previewTexto = preview ? preview.querySelector('.work__preview-fallback span') : null;
  var alvoX = 0, alvoY = 0, atualX = 0, atualY = 0, animando = false;

  if (previewImg) vigiarImagem(previewImg);

  function esconderPreview() {
    if (preview) preview.classList.remove('is-visivel');
  }

  function loopPreview() {
    atualX += (alvoX - atualX) * 0.16;
    atualY += (alvoY - atualY) * 0.16;
    if (preview) {
      preview.style.transform = 'translate3d(' + (atualX - preview.offsetWidth / 2) + 'px,' +
        (atualY - preview.offsetHeight / 2) + 'px,0)' +
        (preview.classList.contains('is-visivel') ? ' scale(1)' : ' scale(0.94)');
    }
    if (Math.abs(alvoX - atualX) > 0.4 || Math.abs(alvoY - atualY) > 0.4) {
      window.requestAnimationFrame(loopPreview);
    } else {
      animando = false;
    }
  }

  if (preview && temMouse && !movimentoReduzido) {
    Array.prototype.forEach.call(document.querySelectorAll('.work__item'), function (item) {
      var botao = item.querySelector('.work__botao');
      if (!botao) return;

      botao.addEventListener('mouseenter', function () {
        if (botao.getAttribute('aria-expanded') === 'true') return;
        var src = item.getAttribute('data-img');
        var nome = item.getAttribute('data-nome') || '';
        if (previewTexto) previewTexto.textContent = nome;
        if (previewImg && previewImg.getAttribute('src') !== src) {
          preview.classList.add('sem-imagem'); /* some com a imagem antiga durante a troca */
          previewImg.setAttribute('src', src);
          previewImg.setAttribute('alt', '');
        }
        preview.classList.add('is-visivel');
      });

      botao.addEventListener('mouseleave', esconderPreview);
    });

    document.addEventListener('mousemove', function (e) {
      alvoX = e.clientX;
      alvoY = e.clientY;
      if (!animando) { animando = true; window.requestAnimationFrame(loopPreview); }
    }, { passive: true });
  }

  /* ----------------------------------------------------------
     CURSOR CUSTOMIZADO (desktop)
     ---------------------------------------------------------- */
  var cursor = document.getElementById('cursor');
  if (cursor && temMouse && !movimentoReduzido) {
    var cx = 0, cy = 0, dx = 0, dy = 0, rodando = false;

    function loopCursor() {
      dx += (cx - dx) * 0.22;
      dy += (cy - dy) * 0.22;
      cursor.style.transform = 'translate3d(' + dx + 'px,' + dy + 'px,0)';
      if (Math.abs(cx - dx) > 0.3 || Math.abs(cy - dy) > 0.3) {
        window.requestAnimationFrame(loopCursor);
      } else {
        rodando = false;
      }
    }

    document.addEventListener('mousemove', function (e) {
      cx = e.clientX; cy = e.clientY;
      cursor.classList.add('is-ativo');
      if (!rodando) { rodando = true; window.requestAnimationFrame(loopCursor); }
    }, { passive: true });

    document.addEventListener('mouseleave', function () { cursor.classList.remove('is-ativo'); });

    /* Cresce sobre qualquer elemento interativo */
    var interativos = 'a, button, [role="button"], input, textarea, select';
    document.addEventListener('mouseover', function (e) {
      if (e.target.closest && e.target.closest(interativos)) cursor.classList.add('is-grande');
    });
    document.addEventListener('mouseout', function (e) {
      if (e.target.closest && e.target.closest(interativos)) cursor.classList.remove('is-grande');
    });
  }

  /* ----------------------------------------------------------
     NÚMEROS — contagem ao entrar na viewport
     Só anima se data-valor for um número de verdade.
     Enquanto for "[SUBSTITUIR]", mostra o texto como está.
     ---------------------------------------------------------- */
  var valores = Array.prototype.slice.call(document.querySelectorAll('.numeros__valor'));

  function contar(el) {
    var bruto = (el.getAttribute('data-valor') || '').trim();
    var sufixo = el.getAttribute('data-sufixo') || '';
    var numero = Number(bruto.replace(/\./g, '').replace(',', '.'));

    if (!bruto || isNaN(numero)) {
      /* Placeholder ainda não preenchido — nada de número inventado */
      el.classList.add('is-placeholder');
      el.textContent = bruto || '[SUBSTITUIR]';
      return;
    }

    if (movimentoReduzido) {
      el.textContent = bruto + sufixo;
      return;
    }

    var duracao = 1400;
    var inicio = null;
    var casas = (bruto.split(/[.,]/)[1] || '').length;

    function passo(agora) {
      if (inicio === null) inicio = agora;
      var t = Math.min((agora - inicio) / duracao, 1);
      var suave = 1 - Math.pow(1 - t, 3); /* easeOutCubic */
      var atual = numero * suave;
      el.textContent = atual.toLocaleString('pt-BR', {
        minimumFractionDigits: casas,
        maximumFractionDigits: casas
      }) + sufixo;
      if (t < 1) window.requestAnimationFrame(passo);
    }
    window.requestAnimationFrame(passo);
  }

  if ('IntersectionObserver' in window) {
    var obsNumeros = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        contar(entrada.target);
        obs.unobserve(entrada.target);
      });
    }, { threshold: 0.4 });
    valores.forEach(function (el) { obsNumeros.observe(el); });
  } else {
    valores.forEach(contar);
  }

  /* ----------------------------------------------------------
     VÍDEOS DO YOUTUBE — lazy-load (o iframe só carrega no clique)
     Para ativar, troque data-youtube pelo ID do vídeo no HTML.
     ---------------------------------------------------------- */
  Array.prototype.forEach.call(document.querySelectorAll('.work__video'), function (caixa) {
    var id = (caixa.getAttribute('data-youtube') || '').trim();

    /* Ainda é placeholder: mostra o aviso e não carrega nada */
    if (!id || id.charAt(0) === '[') {
      var nota = document.createElement('p');
      nota.className = 'work__video-nota';
      nota.textContent = 'Espaço para vídeo — ' + (id || '[SUBSTITUIR: ID do vídeo do YouTube]');
      caixa.appendChild(nota);
      return;
    }

    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'work__video-botao';
    botao.setAttribute('aria-label', 'Carregar e reproduzir o vídeo do YouTube');

    var thumb = document.createElement('img');
    thumb.src = 'https://i.ytimg.com/vi/' + id + '/hqdefault.jpg';
    thumb.alt = '';
    thumb.loading = 'lazy';
    thumb.decoding = 'async';

    var play = document.createElement('span');
    play.className = 'work__video-play';
    play.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false">' +
      '<path d="M8 5l12 7-12 7z" fill="#fff"/></svg>';

    botao.appendChild(thumb);
    botao.appendChild(play);
    caixa.appendChild(botao);

    botao.addEventListener('click', function () {
      var iframe = document.createElement('iframe');
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      iframe.title = 'Vídeo do case no YouTube';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.setAttribute('allowfullscreen', '');
      iframe.loading = 'lazy';
      caixa.replaceChild(iframe, botao);
    });
  });

})();
