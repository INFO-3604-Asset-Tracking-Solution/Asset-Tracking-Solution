importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.5.4/workbox-sw.js');

if (workbox) {
    console.log('Workbox is loaded successfully.');

    // Force the service worker to activate immediately
    workbox.core.skipWaiting();
    workbox.core.clientsClaim();

    // Precache essential static assets and routes for offline access
    workbox.precaching.precacheAndRoute([
        { url: '/static/manifest.json', revision: '1.4' },
        { url: '/static/images/profile_icon.png', revision: '1.4' },
        { url: '/static/images/barcode_icon.svg', revision: '1.4' },
        { url: '/static/images/qrcode_icon.svg', revision: '1.4' },
        { url: '/static/images/rfid_icon.svg', revision: '1.4' },
        { url: '/static/images/manual_icon.svg', revision: '1.4' },
        // Precache CDN dependencies
        { url: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css', revision: '1.4' },
        { url: 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css', revision: '1.4' },
        { url: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', revision: '1.4' },
        { url: 'https://unpkg.com/html5-qrcode', revision: '1.4' },
    ]);

    // Configure Background Sync for API write requests (POST, PUT, DELETE)
    const bgSyncPlugin = new workbox.backgroundSync.BackgroundSyncPlugin('api-sync-queue', {
        maxRetentionTime: 24 * 60, // Retry for max of 24 Hours
    });

    // Handle POST/PUT/DELETE requests with Background Sync
    const syncHandler = new workbox.strategies.NetworkOnly({
        plugins: [bgSyncPlugin]
    });

    workbox.routing.registerRoute(
        ({ url }) => url.pathname.startsWith('/api/'),
        ({ event, request }) => {
            if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
                return syncHandler.handle({ event, request });
            }
        }
    );

    // Cache page navigations and API GET requests using Network First
    workbox.routing.registerRoute(
        ({ request, url }) => {
            return request.mode === 'navigate' ||
                (url.pathname.startsWith('/api/') && request.method === 'GET');
        },
        new workbox.strategies.NetworkFirst({
            cacheName: 'dynamic-content-v2',
            plugins: [
                new workbox.expiration.ExpirationPlugin({
                    maxEntries: 100,
                    maxAgeSeconds: 7 * 24 * 60 * 60, // 1 week
                }),
                new workbox.cacheableResponse.CacheableResponsePlugin({
                    statuses: [0, 200],
                }),
            ],
        })
    );

    // Cache static assets (CSS, JS) using Network First
    workbox.routing.registerRoute(
        ({ request }) => request.destination === 'style' || request.destination === 'script' || request.destination === 'worker',
        new workbox.strategies.NetworkFirst({
            cacheName: 'site-static-v3',
        })
    );

    // Offline fallback for navigation
    workbox.routing.setCatchHandler(async ({ event }) => {
        if (event.request.mode === 'navigate') {
            return (await caches.match('/audit')) ||
                (await caches.match('/inventory')) ||
                (await caches.match('/audit-logs')) ||
                Response.error();
        }
        return Response.error();
    });

} else {
    console.error('Workbox failed to load. Operating without service worker caching and background sync.');
}