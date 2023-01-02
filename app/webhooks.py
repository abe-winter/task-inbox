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

def send_push_key(claims: dict, pem_path: str, key: WebhookKey, body: str, outcomes: Optional[collections.Counter] = None, cleanup: list = None) -> Optional[Exception]:
    "do push to individual key, clean up key if necessary"
    url = urllib.parse.urlparse(key.subscription_blob['endpoint'])
    err_outer = None
    try:
        # todo: urgency=high header maybe https://web.dev/push-notifications-web-push-protocol/#urgency
        pywebpush.webpush(
            key.subscription_blob,
            body,
            vapid_private_key=pem_path,
            vapid_claims={**claims, 'aud': f'{url.scheme}://{url.netloc}'},
        )
        outcomes['success'] += 1
    except pywebpush.WebPushException as err:
        if err.response.status_code == 410:
            if cleanup is not None:
                cleanup.append(key)
        else:
            logger.exception('unk WebPushException status %s', err.response and err.response.status_code)
        err_outer = err
    except Exception as err:
        err_outer = err
    if err_outer:
        outcomes['fail'] += 1
        outcomes[type(err_outer)] += 1
    return err_outer

def send_webpush(session: 'sqlalchemy.orm.Session', config, task: Task) -> collections.Counter:
    """Send a webpush to every user on the server (ugh preferences pls) when a task is created.
    Caller should session.commit() afterwards to handle deleted tokens.
    """
    # todo: background task pls with per-service retry semantics maybe
    rows = session.execute(select(WebPushKey)).all()
    logger.info('sending push to %d sessions', len(rows))
    # I have no idea how CWD works in this framework. switch
    vapid_path = raw_vapid \
        if os.path.isabs((raw_vapid := config['VAPID_PATH'])) \
        else os.path.join(os.path.dirname(__file__), raw_vapid)
    claims = json.load(open(os.path.join(vapid_path, 'claims.json')))
    pem_path = os.path.join(vapid_path, 'private_key.pem')
    body = json.dumps({'msg': f'new {task.ttype.name}', 'tag': task.ttype.name})
    outcomes = collections.Counter()
    cleanup = []
    for key, in rows:
        send_push_key(claims, pem_path, key, body, outcomes, cleanup)
    logger.info('push outcomes %s', outcomes)
    if cleanup:
        logger.info('deleting %d stale keys', len(cleanup))
        for key in cleanup:
            session.delete(key)
    return outcomes
