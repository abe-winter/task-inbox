// this is mostly from https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers

self.addEventListener("install", event => {
  event.waitUntil(async () => (await caches.open('v1').addAll([
    '/taskui',
    '/static/js/index.js',
  ])));
});

self.addEventListener('fetch', event => {
  caches.match(event.request).then(response => {
    return response || fetch(event.request);
  });
});
