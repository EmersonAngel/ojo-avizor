// Service worker de Ojo Avizor (RF-23): cachea las páginas visitadas para
// que sigan disponibles si se pierde la conexión mientras se navega. No
// intenta sincronizar datos: eso lo hace static/js/registro-offline.js
// con la cola en localStorage.
const CACHE_NAME = 'ojo-avizor-v1';

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', (evento) => {
    evento.waitUntil(
        caches.keys().then((nombres) =>
            Promise.all(nombres.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (evento) => {
    if (evento.request.method !== 'GET' || evento.request.mode !== 'navigate') {
        return;
    }
    evento.respondWith(
        fetch(evento.request)
            .then((respuesta) => {
                const copia = respuesta.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(evento.request, copia));
                return respuesta;
            })
            .catch(() => caches.match(evento.request))
    );
});
