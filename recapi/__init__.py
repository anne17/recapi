"""Instanciation of flask app."""

import os
import sys
import logging
import time

from flask import Flask
from flask_session import Session
from flask_cors import CORS


def create_app():
    """Instanciate app."""
    # https://github.com/pallets/flask/blob/master/examples/tutorial/flaskr/__init__.py
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Read config
    if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.py')) is False:
        print("Config file 'config.py' is missing! Cannot run application.")
        exit()

    app.config.from_object('config.Config')

    # Set root path (parent dir to recapi package)
    app.config["ROOT_PATH"] = os.path.abspath(os.path.join(app.root_path, os.pardir))

    # Configure logger
    logfmt = '%(asctime)-15s - %(levelname)s: %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    if app.config.get("DEBUG"):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                            format=logfmt, datefmt=datefmt)
    else:
        today = time.strftime("%Y-%m-%d")
        logdir = os.path.join(app.instance_path, "logs")
        logfile = os.path.join(logdir, f"{today}.log")

        # Create log dir if it does not exist
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        # Create log file if it does not exist
        if not os.path.isfile(logfile):
            with open(logfile, "w") as f:
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write("%s CREATED DEBUG FILE\n\n" % now)

        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format=logfmt, datefmt=datefmt)

    # Init session
    Session(app)

    from . import views, parse_html
    app.register_blueprint(views.general)
    app.register_blueprint(parse_html.parser_views)

    return app


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    http://flask.pocoo.org/snippets/35/

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)
