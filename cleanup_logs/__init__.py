import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from .web import process_log

    @app.route('/')
    def root():
        return app.send_static_file('index.html')
    app.register_blueprint(process_log.bp)

    return app
