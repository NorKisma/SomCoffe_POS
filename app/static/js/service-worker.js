const CACHE_NAME = 'somcoffe-pro-v4';
const STATIC_ASSETS = [
  '/pos/',
  '/auth/login',
  '/manifest.json',
  '/static/css/style.css',
  '/static/css/pos.css',
  '/static/js/pos.js',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
  'https://cdn.jsdelivr.net/npm/sweetalert2@11',
  'https://code.jquery.com/jquery-3.7.1.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// Installation: Pre-cache core shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('SW: Pre-caching core shell');
      return Promise.allSettled(
        STATIC_ASSETS.map(url => {
          return fetch(url, { cache: 'reload' }).then(res => {
            if (res.ok) return cache.put(url, res);
            return Promise.reject('Invalid response');
          }).catch(e => console.error('SW: Failed to cache', url));
        })
      );
    })
  );
  self.skipWaiting();
});

// Activation: Cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
  return self.clients.claim();
});

// Fetching: Intelligent Strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Skip non-GET and third-party API calls (e.g., non-static)
  if (request.method !== 'GET') return;

  // 2. Navigation requests: Network-First, Fallback to Cache
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request) || caches.match('/pos/'))
    );
    return;
  }

  // 3. Static Assets: Stale-While-Revalidate
  // Serve from cache immediately, then update cache in background
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const fetchPromise = fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return networkResponse;
      }).catch(() => null);

      return cachedResponse || fetchPromise;
    })
  );
});

// Background Sync (If browser supports it)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-orders') {
    console.log('SW: Background Sync Triggered');
    // Note: The actual sync logic usually happens in the client-side JS (pos.js)
    // by calling Terminal.syncOfflineOrders().
    // We can also postMessage to clients to trigger sync.
    self.clients.matchAll().then(clients => {
      clients.forEach(client => client.postMessage({ type: 'SYNC_ORDERS' }));
    });
  }
});
