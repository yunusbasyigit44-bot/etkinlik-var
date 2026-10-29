// Etkinlik Var — çevrimdışı desteği (uygulama ve "ana ekrana ekle" için).
// Sayfa ve etkinlik listeleri: önce internetten, olmazsa son kaydedilen hâl.
// Simgeler ve afişler: önce kayıttan (hızlı açılış). Başka sitelere giden isteklere karışılmaz.
const SURUM = "ev-1";
const ONCEDEN = ["/", "/index.html", "/manifest.webmanifest", "/ikon/ikon-192.png", "/ikon/ikon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SURUM).then(c => c.addAll(ONCEDEN)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(a => a !== SURUM).map(a => caches.delete(a))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const istek = e.request, url = new URL(istek.url);
  if(istek.method !== "GET" || url.origin !== location.origin) return;
  const gorselMi = /\.(png|jpe?g|webp|gif|svg)$/i.test(url.pathname);
  if(gorselMi){
    e.respondWith(caches.match(istek).then(k => k || fetch(istek).then(c => {
      if(c.ok){ const kopya = c.clone(); caches.open(SURUM).then(o => o.put(istek, kopya)); }
      return c;
    })));
    return;
  }
  e.respondWith(fetch(istek).then(c => {
    if(c.ok){ const kopya = c.clone(); caches.open(SURUM).then(o => o.put(istek, kopya)); }
    return c;
  }).catch(() => caches.match(istek, {ignoreSearch: istek.mode === "navigate"})
    .then(k => k || (istek.mode === "navigate" ? caches.match("/") : Response.error()))));
});
