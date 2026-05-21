from app import create_app, db
from app.models import User, Post
from app.config import DevConfig
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

app = create_app(DevConfig)

ERROR_COUNTER = Counter('app_errors_total', 'Total errors in app')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/fail")
def fail():
    raise Exception("Test error for monitoring")

@app.errorhandler(Exception)
def handle_exception(e):
    ERROR_COUNTER.inc()
    raise e