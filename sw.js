const CACHE_NAME = "sabana-cache-v1";
const urlsToCache = [
  "/",
  "/manifest.json",
  "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css",
  "https://unpkg.com/dexie/dist/dexie.js",
  "https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"
];

// Instalar y guardar en caché
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Interceptar peticiones (Si no hay internet, sirve desde el caché)
self.addEventListener("fetch", event => {
  if (event.request.method !== 'GET') return; // No interceptar POSTs
  
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});