import logging, os
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

@app.get('/health')
def get_health():
    return {
        'version': os.environ.get('DOCKER_TAG'),
    }

class IntentionalError(Exception):
    "for testing sentry"

@app.get('/crash')
def get_crash():
    raise IntentionalError

# sigh, circular import from boilerplate
from . import views, schemaviews
