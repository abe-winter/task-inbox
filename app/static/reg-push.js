/** register web push */

// adapted from https://github.com/mdn/serviceworker-cookbook/blob/master/push-simple/index.js
async function regPush() {
  const reg = await navigator.serviceWorker.ready;
  let sub = await reg.pushManager.getSubscription();
  if (!sub) {
    const applicationServerKey = (await fetch('/.vapid-pk').then(res => {
      if (res.status != 200) throw Error(res.status.toString());
      return res.text();
    })).trim();
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey,
    });
  }
  await fetch('/push/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sub }),
  });
}

if (navigator.serviceWorker) regPush();
