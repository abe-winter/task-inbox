from typing import Optional
import flask, requests, urllib.parse
from sqlalchemy import text
from backend.taskschema import HookAuth
from .models import Task, WebhookKey

def run_webhook(session: 'sqlalchemy.orm.Session', task: Task) -> Optional[requests.Response]:
    "if task is associated with a webhook, call it"
    version = task.ttype.version
    if not version.default_hook_url:
        return None
    hook_auth = HookAuth.parse_obj(version.hook_auth)
    key = session.query(WebhookKey) \
        .filter_by(tschema=version.tschema, hook_auth=version.hook_auth) \
        .order_by(text('created desc')) \
        .first()
    if not key:
        flask.abort(flask.Response("can't run webhook, missing webhook_key", status=501))
    url = urllib.parse.urlparse(version.default_hook_url).geturl()
    # todo: let vendors ask for custom bodies
    body = {**task.jsonable(), 'ttype': task.ttype.name}
    if hook_auth.kind == 'head':
        res = requests.post(url, json=body, headers={hook_auth.val: key.key})
    else:
        raise NotImplementedError(f'unk hook_auth.kind {hook_auth.kind}')
    res.raise_for_status()
    # todo: anything we want to log or capture back about webhook? (maybe log which URL hit, which key, status code at least)
    return res
