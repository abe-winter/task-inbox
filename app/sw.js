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
  event.waitUntil(self.registration.showNotification('task-inbox', {
    body: body.msg,
    tag: body.tag, // for merging by type I think
    renotify: !!body.tag, // so merged msgs still ping. error if tag is null, hence !!
    requireInteraction: true, // i.e. don't auto-vanish
  }));
});

addEventListener('notificationclick', event => {
  console.log('click', event);
  event.notification.close();
  event.waitUntil(async () => {
    for (const client of await clients.matchAll({ type: 'window' })) {
      console.log('client', client);
      if ('focus' in client) return client.focus();
    }
    if (clients.openWindow) return clients.openWindow('/');
  });
});
