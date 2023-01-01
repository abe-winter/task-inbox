"flask app for webhook receiver"
import os, functools
import flask

RCV_HOOK_KEY = os.environ.get('RCV_HOOK_KEY')

app = flask.Flask(__name__)

def hook_key(header='ti-key'):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not RCV_HOOK_KEY: flask.abort(501)
            if header not in flask.request.headers: flask.abort(401)
            if flask.request.headers[header] != RCV_HOOK_KEY: flask.abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/v1/tihook', methods=['POST'])
@hook_key()
def post_tihook():
    print('inbound hook', flask.request.json)
    return 'ok'
