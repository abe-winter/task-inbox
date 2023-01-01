import functools
import flask
from sqlalchemy import select
from .main import appbuilder
from .models import ApiKey

def apikey_auth_inner() -> ApiKey:
    "non-decorator logic for header check -> flask.g state / error"
    session = appbuilder.get_session()
    if 'api-key' not in flask.request.headers:
        flask.abort(flask.Response("missing api-key header", status=401))
    # todo: filter active here
    key = session.get(ApiKey, flask.request.headers['api-key'])
    if key is None:
        flask.abort(flask.Response("unknown or expired API key", status=403))
    flask.g.apikey_auth = key
    return key

def apikey_auth():
    """Decorator to require an active API key in the api-key header.
    Sets flask.g.apikey_auth if successful, throws 401 if not.
    note: you may still need to check the specific roles inside the function.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            apikey_auth_inner()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
