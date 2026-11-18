const CACHE_NAME = "injabulo-clinic-static-v2";

const STATIC_ASSETS = [
    "/static/core/css/style.css",
    "/static/core/images/injabulo-clinic-logo.png",
    "/static/core/images/icon-192.png",
    "/static/core/images/icon-512.png",
    "/static/core/pwa/offline.html"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key =>
                        key.startsWith("injabulo-clinic-") &&
                        key !== CACHE_NAME
                    )
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {
    const request = event.request;
    const url = new URL(request.url);

    if (
        request.method !== "GET" ||
        url.origin !== self.location.origin
    ) {
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(async () => {
                const cache = await caches.open(CACHE_NAME);
                return await cache.match(
                    "/static/core/pwa/offline.html"
                );
            })
        );
        return;
    }

    if (url.pathname.startsWith("/static/")) {
        const isStyleOrScript =
            /\.(css|js)$/i.test(url.pathname);

        if (isStyleOrScript) {
            event.respondWith(
                fetch(request).then(response => {
                    if (response.ok) {
                        const copy = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => cache.put(request, copy));
                    }
                    return response;
                }).catch(async () => {
                    return await caches.match(request);
                })
            );
        } else {
            event.respondWith(
                caches.match(request).then(cached => {
                    if (cached) return cached;

                    return fetch(request).then(response => {
                        if (response.ok) {
                            const copy = response.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(request, copy));
                        }
                        return response;
                    });
                })
            );
        }
    }
});
