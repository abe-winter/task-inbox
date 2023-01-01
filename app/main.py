import logging, os, flask
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_appbuilder import AppBuilder, SQLA

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")
app.wsgi_app = ProxyFix(app.wsgi_app)
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

@app.get('/health')
def get_health():
    return {
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
    raise IntentionalError

# sigh, circular import from boilerplate
from . import views, schemaviews
