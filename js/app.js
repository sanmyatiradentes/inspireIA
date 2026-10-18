// InspireIA — instalação como app no celular/computador.
(function () {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });
  }

  var pedido = null;  // evento do Chrome/Android que abre a instalação
  var instalado = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  var ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

  function botoes() { return document.querySelectorAll('.btn-instalar'); }
  function mostrar(sim) { botoes().forEach(function (b) { b.hidden = !sim; }); }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); pedido = e; mostrar(true);
  });
  window.addEventListener('appinstalled', function () { pedido = null; mostrar(false); });

  function ajudaIos() {
    var caixa = document.getElementById('ajuda-instalar');
    if (caixa) caixa.hidden = false;
  }

  document.addEventListener('click', function (e) {
    if (e.target.closest('.btn-instalar')) {
      if (pedido) { pedido.prompt(); pedido.userChoice.then(function () { pedido = null; mostrar(false); }); }
      else ajudaIos();
    }
    if (e.target.closest('[data-fechar-ajuda]')) document.getElementById('ajuda-instalar').hidden = true;
  });

  document.addEventListener('DOMContentLoaded', function () {
    // No iPhone não existe o aviso automático: o botão mostra o passo a passo.
    mostrar(!instalado && ios);
  });
})();

// Botão flutuante do WhatsApp: some enquanto o aviso de privacidade está aberto
// e quando o chat está na tela (no celular ele cobriria o campo de digitar).
(function () {
  function iniciar() {
    var fab = document.getElementById('waFab'), banner = document.getElementById('consent-banner'), chat = document.getElementById('ferramenta');
    if (!fab) return;
    var chatVisivel = false;
    function atualizar() {
      var bannerAberto = banner && !banner.classList.contains('hidden');
      fab.classList.toggle('oculto', bannerAberto || chatVisivel);
    }
    if (chat && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { chatVisivel = e[0].isIntersecting; atualizar(); }, {threshold: 0.15}).observe(chat);
    }
    if (banner && 'MutationObserver' in window) new MutationObserver(atualizar).observe(banner, {attributes: true});
    atualizar();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
