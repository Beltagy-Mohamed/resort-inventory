const CACHE_NAME = 'ordinance-offline-cache-v1';
const OFFLINE_URL = '/offline/';

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll([
                OFFLINE_URL,
                '/static/images/logo.jpg',
                '/static/css/base.css'
            ]);
        })
    );
});

self.addEventListener('fetch', event => {
    // Only handle GET requests for HTML documents
    if (event.request.method === 'GET' && event.request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(event.request).catch(error => {
                // If network fails, serve the offline page
                return caches.match(OFFLINE_URL);
            })
        );
    }
});
