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

self.addEventListener('pushsubscriptionchange', event => {
  console.warn('todo: handle pushsubscriptionchange');
});

self.addEventListener('push', event => {
  const body = event.data.json();
  event.waitUntil(self.registration.showNotification('task-inbox', { body: body.msg }));
});
