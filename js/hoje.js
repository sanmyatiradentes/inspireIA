// InspireIA — Seu dia (devocional, sabedoria estoica, aprendizado por área),
// trilhas de 21 dias e "Ouvir o dia". Conteúdo fixo em conteudo/diario.js.
// Nada aqui é enviado a servidor: o progresso fica no localStorage do aparelho.

(function () {
  var C = window.INSPIRE_CONTEUDO;
  if (!C) return;

  var MESES = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
  var SEMANA = ['domingo','segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado'];
  var desloc = 0;          // dias de distância de hoje (setas ‹ ›)
  var areaAtual = C.areas[0].area_id;

  // --- utilitários ---

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function $(id) { return document.getElementById(id); }

  function hojeLocal(d) {
    d = d || new Date();
    return new Date(d.getFullYear(), d.getMonth(), d.getDate());
  }
  function chaveData(d) {
    return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  }
  // Número do dia contado a partir de 1/1/2026 — todos veem o mesmo conteúdo no mesmo dia.
  function numeroDia(d) {
    return Math.round((hojeLocal(d) - new Date(2026, 0, 1)) / 86400000);
  }
  function item(lista, n) { return lista[((n % lista.length) + lista.length) % lista.length]; }

  function ler(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v ? JSON.parse(v) : padrao; } catch (e) { return padrao; }
  }
  function gravar(chave, v) {
    try { localStorage.setItem(chave, JSON.stringify(v)); } catch (e) {}
  }

  function dataDoDia() {
    var d = hojeLocal(); d.setDate(d.getDate() + desloc); return d;
  }

  // --- Sequência de dias (visitas) ---

  function registrarVisita() {
    var v = ler('inspireia_visitas', {ultimo: null, seq: 0});
    var hoje = chaveData(hojeLocal());
    if (v.ultimo === hoje) return v.seq;
    var ontem = hojeLocal(); ontem.setDate(ontem.getDate() - 1);
    v.seq = (v.ultimo === chaveData(ontem)) ? v.seq + 1 : 1;
    v.ultimo = hoje;
    gravar('inspireia_visitas', v);
    return v.seq;
  }

  // --- Conversar com a mentora sobre um conteúdo ---

  window.inspireConversar = function (texto) {
    var input = $('user-input');
    if (!input) return;
    input.value = texto;
    input.dispatchEvent(new Event('input'));
    var f = $('ferramenta');
    if (f) f.scrollIntoView({behavior: 'smooth'});
    setTimeout(function () { input.focus(); }, 600);
  };

  // --- Seção "Hoje" ---

  function renderHoje() {
    var d = dataDoDia(), n = numeroDia(d);
    var dev = item(C.devocional, n), est = item(C.estoico, n);

    $('hoje-data').textContent = SEMANA[d.getDay()] + ', ' + d.getDate() + ' de ' + MESES[d.getMonth()];
    $('hoje-rotulo').textContent = desloc === 0 ? 'Hoje' : (desloc === -1 ? 'Ontem' : (desloc === 1 ? 'Amanhã' : (desloc < 0 ? 'Há ' + (-desloc) + ' dias' : 'Daqui a ' + desloc + ' dias')));
    $('hoje-voltar-hoje').style.visibility = desloc === 0 ? 'hidden' : 'visible';

    var url = 'https://www.bibliaonline.com.br/ntlh/' + dev.livro_slug + '/' + dev.capitulo;
    $('card-devocional').innerHTML =
      '<div class="hj-tag">📖 Devocional</div>' +
      '<h3 class="hj-tit">' + esc(dev.tema) + '</h3>' +
      '<a class="hj-ref" href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(dev.referencia) + ' <span>· ler na NTLH ↗</span></a>' +
      '<p class="hj-ideia">' + esc(dev.ideia_central) + '</p>' +
      '<p>' + esc(dev.reflexao) + '</p>' +
      '<div class="hj-oracao"><strong>Oração</strong><p>' + esc(dev.oracao) + '</p></div>' +
      '<div class="hj-acao"><strong>Ação de hoje</strong><p>' + esc(dev.acao) + '</p></div>' +
      '<div class="hj-botoes">' +
        '<button class="hj-btn" data-ouvir="dev">🎧 Ouvir</button>' +
        '<button class="hj-btn" data-conversar="dev">💬 Conversar sobre isso</button>' +
      '</div>';

    $('card-estoico').innerHTML =
      '<div class="hj-tag">🏛️ Sabedoria estoica</div>' +
      '<blockquote class="hj-frase">' + esc(est.frase) + '</blockquote>' +
      '<div class="hj-autor">' + esc(est.autor) + ' — <em>' + esc(est.obra) + '</em></div>' +
      '<p>' + esc(est.aplicacao) + '</p>' +
      '<div class="hj-acao"><strong>Exercício</strong><p>' + esc(est.pratica) + '</p></div>' +
      '<div class="hj-botoes">' +
        '<button class="hj-btn" data-ouvir="est">🎧 Ouvir</button>' +
        '<button class="hj-btn" data-conversar="est">💬 Conversar</button>' +
      '</div>';

    renderAreas();
  }

  function renderAreas() {
    var n = numeroDia(dataDoDia());
    $('hj-abas').innerHTML = C.areas.map(function (a) {
      return '<button class="hj-aba' + (a.area_id === areaAtual ? ' ativa' : '') + '" data-area="' + esc(a.area_id) + '">' + esc(a.area_nome) + '</button>';
    }).join('');
    var ativa = $('hj-abas').querySelector('.ativa');
    if (ativa) $('hj-abas').scrollLeft = ativa.offsetLeft - $('hj-abas').offsetLeft - 16;
    var area = C.areas.filter(function (a) { return a.area_id === areaAtual; })[0];
    var l = item(area.licoes, n);
    $('card-area').innerHTML =
      '<div class="hj-tag">' + esc(area.area_nome) + '</div>' +
      '<h3 class="hj-tit">' + esc(l.titulo) + '</h3>' +
      '<div class="hj-autor">' + esc(l.fonte) + '</div>' +
      '<p>' + esc(l.ideia) + '</p>' +
      '<div class="hj-acao"><strong>Pratique hoje</strong><p>' + esc(l.pratica) + '</p></div>' +
      '<p class="hj-pergunta">' + esc(l.pergunta) + '</p>' +
      '<div class="hj-botoes">' +
        '<button class="hj-btn" data-ouvir="area">🎧 Ouvir</button>' +
        '<button class="hj-btn" data-conversar="area">💬 Conversar sobre isso</button>' +
      '</div>';
  }

  function conteudoAtual() {
    var n = numeroDia(dataDoDia());
    var area = C.areas.filter(function (a) { return a.area_id === areaAtual; })[0];
    return {dev: item(C.devocional, n), est: item(C.estoico, n), area: area, licao: item(area.licoes, n), n: n};
  }

  // --- Ouvir (voz do navegador) ---

  var falando = false;

  function vozPt() {
    var vozes = speechSynthesis.getVoices().filter(function (v) { return /^pt(-|_)BR/i.test(v.lang); });
    var pref = ['Luciana', 'Google português do Brasil', 'Francisca', 'Thalita', 'Microsoft Maria'];
    for (var i = 0; i < pref.length; i++) {
      var v = vozes.filter(function (x) { return x.name.indexOf(pref[i]) === 0; })[0];
      if (v) return v;
    }
    return vozes[0] || null;
  }

  // O Chrome corta falas longas; por isso a leitura vai em frases curtas, uma após a outra.
  function falar(blocos, botao) {
    if (!('speechSynthesis' in window)) { alert('Seu navegador não tem leitura em voz alta.'); return; }
    if (falando) { pararFala(); return; }
    var frases = [];
    blocos.forEach(function (b) {
      (String(b).match(/[^.!?…]+[.!?…]*/g) || []).forEach(function (f) { f = f.trim(); if (f) frases.push(f); });
    });
    var voz = vozPt();
    falando = true;
    marcarBotoes(botao, true);
    frases.forEach(function (f, i) {
      var u = new SpeechSynthesisUtterance(f);
      u.lang = 'pt-BR'; u.rate = 0.98;
      if (voz) u.voice = voz;
      if (i === frases.length - 1) u.onend = function () { falando = false; marcarBotoes(null, false); };
      speechSynthesis.speak(u);
    });
  }
  function pararFala() {
    speechSynthesis.cancel();
    falando = false;
    marcarBotoes(null, false);
  }
  function marcarBotoes(botao, ativo) {
    document.querySelectorAll('[data-ouvir],#hj-ouvir-dia').forEach(function (b) {
      b.classList.remove('falando');
      if (b.dataset.rotulo) { b.textContent = b.dataset.rotulo; delete b.dataset.rotulo; }
    });
    if (ativo && botao) {
      botao.dataset.rotulo = botao.textContent;
      botao.textContent = '⏹ Parar';
      botao.classList.add('falando');
    }
  }

  function roteiro(qual) {
    var c = conteudoAtual();
    if (qual === 'dev') return ['Devocional. ' + c.dev.tema + '.', 'Leitura: ' + c.dev.referencia + '.', c.dev.ideia_central, c.dev.reflexao, 'Oração. ' + c.dev.oracao, 'Ação de hoje. ' + c.dev.acao];
    if (qual === 'est') return ['Sabedoria estoica. ' + c.est.autor + ' disse:', c.est.frase, c.est.aplicacao, 'Exercício. ' + c.est.pratica];
    if (qual === 'area') return [c.area.area_nome + '. ' + c.licao.titulo + '.', 'Inspirado em ' + c.licao.fonte + '.', c.licao.ideia, 'Pratique hoje. ' + c.licao.pratica, 'Para refletir. ' + c.licao.pergunta];
    // Dia completo, no formato de um pequeno podcast.
    var d = dataDoDia();
    var partes = ['Olá! Aqui é a InspireIA, com o seu dia. ' + SEMANA[d.getDay()] + ', ' + d.getDate() + ' de ' + MESES[d.getMonth()] + '.']
      .concat(roteiro('dev'))
      .concat(roteiro('est'));
    C.areas.forEach(function (a) {
      var l = item(a.licoes, c.n);
      partes.push(a.area_nome + '. ' + l.titulo + '.', l.ideia, 'Pratique hoje. ' + l.pratica);
    });
    partes.push('Isso é tudo por hoje. Um passo pequeno, todo dia, muda uma vida. Até amanhã!');
    return partes;
  }

  function textoConversa(qual) {
    var c = conteudoAtual();
    if (qual === 'dev') return 'Li o devocional de hoje, "' + c.dev.tema + '" (' + c.dev.referencia + '). Me ajuda a aplicar isso na minha vida? Minha situação é: ';
    if (qual === 'est') return 'Li a sabedoria estoica de hoje (' + c.est.autor + ': "' + c.est.frase + '"). Como aplico isso no que estou vivendo? Minha situação é: ';
    return 'Li o aprendizado de hoje em ' + c.area.area_nome + ': "' + c.licao.titulo + '" (' + c.licao.fonte + '). Como aplico isso no meu caso? ';
  }

  // --- Trilhas de 21 dias ---

  function estadoTrilhas() { return ler('inspireia_trilhas', {}); }

  // Índice do dia em foco: o que foi feito hoje, senão o próximo a fazer (ou o último, se concluída).
  function diaAtualTrilha(s) {
    if (!s) return 0;
    var n = s.feitos.length;
    if (s.feitos.indexOf(chaveData(hojeLocal())) !== -1) return n - 1;
    return Math.min(n, 20);
  }

  function renderTrilhas() {
    var est = estadoTrilhas();
    $('tr-lista').innerHTML = C.trilhas.map(function (t) {
      var s = est[t.id], feitos = s ? s.feitos.length : 0;
      var status = !s ? 'Começar trilha' : (feitos >= 21 ? '✓ Concluída' : 'Continuar · dia ' + (feitos + 1));
      return '<div class="tr-card' + (s ? ' iniciada' : '') + '">' +
        '<div class="tr-nome">' + esc(t.nome) + '</div>' +
        '<div class="tr-sub">' + esc(t.subtitulo) + '</div>' +
        '<div class="tr-para">' + esc(t.para_quem) + '</div>' +
        '<div class="tr-fontes">' + esc(t.fontes) + '</div>' +
        '<div class="tr-barra"><span style="width:' + Math.round(feitos / 21 * 100) + '%"></span></div>' +
        '<button class="hj-btn tr-abrir" data-trilha="' + esc(t.id) + '">' + status + '</button>' +
      '</div>';
    }).join('');
  }

  function abrirTrilha(id) {
    var t = C.trilhas.filter(function (x) { return x.id === id; })[0];
    var est = estadoTrilhas(), s = est[id];
    if (!s) { s = est[id] = {inicio: chaveData(hojeLocal()), feitos: []}; gravar('inspireia_trilhas', est); renderTrilhas(); }
    var feitos = s.feitos.length;
    var jaFezHoje = s.feitos.indexOf(chaveData(hojeLocal())) !== -1;
    var atual = diaAtualTrilha(s);
    var dia = t.dias[atual];

    var acoes;
    if (feitos >= 21) acoes = '<p class="tr-msg">🎉 Você concluiu os 21 dias. Isso já faz parte de quem você é.</p>';
    else if (jaFezHoje) acoes = '<p class="tr-msg">✓ Feito hoje. O dia ' + (feitos + 1) + ' libera amanhã — hábito se constrói com constância, não com pressa.</p>';
    else acoes = '<button class="btn-primary tr-feito" data-feito="' + esc(id) + '">✓ Fiz hoje</button>';

    $('tr-detalhe').innerHTML =
      '<button class="tr-fechar" data-fechar="1" aria-label="Fechar">×</button>' +
      '<div class="hj-tag">Trilha de 21 dias</div>' +
      '<h3 class="hj-tit">' + esc(t.nome) + '</h3>' +
      '<div class="tr-barra grande"><span style="width:' + Math.round(feitos / 21 * 100) + '%"></span></div>' +
      '<div class="tr-cont">' + feitos + ' de 21 dias</div>' +
      '<div class="tr-dia">' +
        '<div class="tr-dia-num">Dia ' + (atual + 1) + '</div>' +
        '<h4>' + esc(dia.titulo) + '</h4>' +
        '<p>' + esc(dia.acao) + '</p>' +
        '<p class="tr-pq"><strong>Por quê:</strong> ' + esc(dia.por_que) + '</p>' +
        acoes +
      '</div>' +
      '<div class="tr-mapa">' + t.dias.map(function (d, i) {
        var cls = i < feitos ? 'ok' : (i === atual ? 'agora' : '');
        return '<span class="' + cls + '" title="Dia ' + (i + 1) + ' — ' + esc(d.titulo) + '">' + (i < feitos ? '✓' : i + 1) + '</span>';
      }).join('') + '</div>' +
      '<div class="hj-botoes">' +
        '<button class="hj-btn" data-conversa-trilha="' + esc(id) + '">💬 Conversar sobre este dia</button>' +
        '<button class="hj-btn discreto" data-recomecar="' + esc(id) + '">Recomeçar trilha</button>' +
      '</div>';
    $('tr-detalhe').classList.add('aberto');
    $('tr-detalhe').scrollIntoView({behavior: 'smooth', block: 'nearest'});
  }

  function marcarFeito(id) {
    var est = estadoTrilhas(), s = est[id];
    var hoje = chaveData(hojeLocal());
    if (!s || s.feitos.indexOf(hoje) !== -1 || s.feitos.length >= 21) return;
    s.feitos.push(hoje);
    gravar('inspireia_trilhas', est);
    renderTrilhas();
    abrirTrilha(id);
  }

  // --- Eventos ---

  document.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    if (b.id === 'hoje-ant') { desloc--; pararFala(); renderHoje(); }
    else if (b.id === 'hoje-prox') { desloc++; pararFala(); renderHoje(); }
    else if (b.id === 'hoje-voltar-hoje') { desloc = 0; pararFala(); renderHoje(); }
    else if (b.id === 'hj-ouvir-dia') falar(roteiro('dia'), b);
    else if (b.dataset.ouvir) falar(roteiro(b.dataset.ouvir), b);
    else if (b.dataset.conversar) inspireConversar(textoConversa(b.dataset.conversar));
    else if (b.dataset.area) { areaAtual = b.dataset.area; pararFala(); renderAreas(); }
    else if (b.dataset.trilha) abrirTrilha(b.dataset.trilha);
    else if (b.dataset.feito) marcarFeito(b.dataset.feito);
    else if (b.dataset.fechar) $('tr-detalhe').classList.remove('aberto');
    else if (b.dataset.recomecar) {
      if (!confirm('Recomeçar esta trilha do dia 1? O progresso atual será zerado.')) return;
      var est = estadoTrilhas(); delete est[b.dataset.recomecar]; gravar('inspireia_trilhas', est);
      renderTrilhas(); abrirTrilha(b.dataset.recomecar);
    }
    else if (b.dataset.conversaTrilha) {
      var t = C.trilhas.filter(function (x) { return x.id === b.dataset.conversaTrilha; })[0];
      var i = diaAtualTrilha(estadoTrilhas()[t.id]);
      inspireConversar('Estou na trilha "' + t.nome + '", dia ' + (i + 1) + ': "' + t.dias[i].titulo + '". Como faço isso bem na minha realidade? ');
    }
  });

  function iniciar() {
    var seq = registrarVisita();
    $('hoje-seq').textContent = seq > 1 ? '🔥 ' + seq + ' dias seguidos' : '✨ Comece sua sequência hoje';
    renderHoje();
    renderTrilhas();
    if ('speechSynthesis' in window) speechSynthesis.getVoices(); // pré-carrega as vozes
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
