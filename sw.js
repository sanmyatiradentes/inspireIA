// InspireIA — service worker: deixa o site instalável e o conteúdo do dia disponível sem internet.
// Sempre busca a versão nova na rede; o cache só entra quando não há conexão. O chat (/api) nunca é guardado.
const CACHE = 'inspireia-v2';
const BASE = ['/', '/css/hoje.css', '/js/hoje.js', '/js/app.js', '/conteudo/diario.js', '/img/inspireia-simbolo.svg', '/img/icone-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
  e.respondWith(
    fetch(e.request)
      .then(r => {
        if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); }
        return r;
      })
      .catch(() => caches.match(e.request, {ignoreSearch: true}).then(r => r || caches.match('/')))
  );
});
