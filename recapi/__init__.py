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

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Read config
    if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.py')) is False:
        print("Config file 'config.py' is missing! Cannot run application.")
        exit()

    app.config.from_object('config.Config')

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
