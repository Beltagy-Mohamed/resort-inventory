/**
 * service-worker.js — Resort Inventory PWA
 *
 * الاستراتيجية (مقصودة، مش افتراضية):
 * - الصفحات الديناميكية وبيانات API: Network-First 
 * - الملفات الثابتة (CSS/JS/الخطوط/الأيقونات): Cache-First
 * - صفحة Offline بديلة
 */

const CACHE_VERSION = "v1.0.1";
const STATIC_CACHE = `resort-inventory-static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `resort-inventory-runtime-${CACHE_VERSION}`;

const STATIC_ASSETS = [
  "/static/pwa/manifest.json",
  "/static/css/base.css",
  "/static/css/dashboard.css",
  "/static/css/product-detail.css",
  "/static/css/products.css",
  "/static/js/layout.js",
  "/offline/",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== RUNTIME_CACHE)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);
  const isStaticAsset = /\.(css|js|png|jpg|jpeg|svg|woff2?|ico)$/.test(url.pathname);

  if (isStaticAsset) {
    event.respondWith(cacheFirst(request));
  } else {
    event.respondWith(networkFirst(request));
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, response.clone());
    return response;
  } catch (err) {
    return cached || Response.error();
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return caches.match("/offline/");
  }
}
