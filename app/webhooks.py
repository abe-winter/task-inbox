import urllib.parse, collections, logging, json, os
from typing import Optional
import flask, requests, pywebpush
from sqlalchemy import text, select
from backend.taskschema import HookAuth
from .models import Task, WebhookKey, WebPushKey

logger = logging.getLogger(__name__)

def run_webhook(session: 'sqlalchemy.orm.Session', task: Task) -> Optional[requests.Response]:
    "if task is associated with a webhook, call it"
    version = task.ttype.version
    if not version.default_hook_url:
        return None
    hook_auth = HookAuth.parse_obj(version.hook_auth)
    # todo: filter active
    # todo: select btwn multiple active keys, but preserve 501 behavior if 0 active
    key = session.query(WebhookKey) \
        .filter_by(tschema=version.tschema, hook_auth=version.hook_auth) \
        .order_by(text('created desc')) \
        .first()
    if not key:
        flask.abort(flask.Response("can't run webhook, missing webhook_key", status=501))
    url = urllib.parse.urlparse(version.default_hook_url).geturl()
    # todo: let vendors ask for custom bodies
    body = {**task.jsonable(), 'ttype': task.ttype.name}
    # todo: 502 and 503 here
    if hook_auth.kind == 'head':
        res = requests.post(url, json=body, headers={hook_auth.val: key.key})
    else:
        raise NotImplementedError(f'unk hook_auth.kind {hook_auth.kind}')
    res.raise_for_status()
    # todo: anything we want to log or capture back about webhook? (maybe log which URL hit, which key, status code at least)
    return res

def send_webpush(session: 'sqlalchemy.orm.Session', config, task: Task):
    "send a webpush to every user on the server (ugh preferences pls) when a task is created"
    # todo: background task pls with per-service retry semantics maybe
    rows = session.execute(select(WebPushKey)).all()
    logger.info('sending push to %d sessions', len(rows))
    # I have no idea how CWD works in this framework. switch
    vapid_path = raw_vapid \
        if os.path.isabs((raw_vapid := config['VAPID_PATH'])) \
        else os.path.join(os.path.dirname(__file__), raw_vapid)
    claims = json.load(open(os.path.join(vapid_path, 'claims.json')))
    message = f'new {task.ttype.name}'
    outcomes = collections.Counter()
    for key, in rows:
        url = urllib.parse.urlparse(key.subscription_blob['endpoint'])
        try:
            pywebpush.webpush(
                key.subscription_blob,
                json.dumps({'msg': message, 'tag': task.ttype.name}),
                vapid_private_key=os.path.join(vapid_path, 'private_key.pem'),
                vapid_claims={**claims, 'aud': f'{url.scheme}://{url.netloc}'},
            )
            outcomes['success'] += 1
        except Exception as err:
            outcomes['fail'] += 1
            outcomes[type(err)] += 1
    logger.info('push outcomes %s', outcomes)
    return outcomes
