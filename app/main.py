import logging, os, base64, binascii
from datetime import datetime
import flask
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.api import protect
from .models import WebPushKey

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")
app.wsgi_app = ProxyFix(app.wsgi_app)
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

@app.before_request
def make_session_permanent():
    # sigh -- is there really no configurable way to preserve logins across browser restart. ugh
    flask.session.permanent = True

@app.get('/health')
def get_health():
    return {
        # client_ip is still wrong -- it's the address of the load balancer now. fix ProxyFix?
        'client_ip': flask.request.remote_addr,
        # these are to make sure flask isn't stripping https
        'health_url': flask.url_for('get_health'),
        'health_url_ext': flask.url_for('get_health', _external=True),
        'version': os.environ.get('DOCKER_TAG'),
    }

class IntentionalError(Exception):
    "for testing sentry"

@app.get('/crash')
def get_crash():
    print(flask.session)
    raise IntentionalError

@app.get('/manifest.json')
def get_manifest():
    return flask.send_file('manifest.json')

@app.get('/sw.js')
def get_service_worker():
    return flask.send_file('sw.js')

@app.get('/.vapid-pk')
def get_vapid_public_key():
    enc = flask.request.args.get('enc')
    # todo: does this need to be signed per-request so expiration is non-null?
    pem_path = os.path.join(app.config['VAPID_PATH'], 'applicationServerKey.b64')
    return flask.send_file(pem_path, mimetype='application/base64')

@app.post('/push/register')
def post_push_register():
    "register for web push"
    session_id = base64.b64encode(binascii.unhexlify(flask.session['_id'])).decode()
    session = appbuilder.get_session
    existing = session.get(WebPushKey, session_id)
    if existing:
        if existing.user_id != flask.g.user.id:
            # todo: siem log
            flask.abort(flask.Response("user ID for session seems to have changed", status=400))
        existing.subscription_blob = flask.request.json['sub']
        existing.updated = datetime.now()
        # session.add(existing)
    else:
        session.add(WebPushKey(
            session_id=session_id,
            user_id=flask.g.user.id,
            subscription_blob=flask.request.json['sub'],
        ))
    session.commit()
    return 'ok'

# sigh, circular import from boilerplate
from . import views, schemaviews
