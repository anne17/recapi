"""Instanciation of flask app."""

import logging
import os
import sys
import time

from flask import Flask
from flask_cors import CORS
from flask_session import Session

from recapi import utils
from recapi.models import usermodel
from recapi.models import recipemodel
from recapi.models import tagmodel


def create_app():
    """Instanciate app."""
    # https://github.com/pallets/flask/blob/master/examples/tutorial/flaskr/__init__.py
    app = Flask(__name__)

    # Prevent flask from resorting JSON
    app.config["JSON_SORT_KEYS"] = False

    # Fix SCRIPT_NAME when proxied
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Set default config
    app.config.from_object("config")

    # Overwrite with instance config
    if os.path.exists(os.path.join(app.instance_path, "config.py")):
        app.config.from_pyfile(os.path.join(app.instance_path, "config.py"))

    # Set root path (parent dir to recapi package)
    app.config["ROOT_PATH"] = os.path.abspath(os.path.join(app.root_path, os.pardir))

    # Configure logger
    logfmt = "%(asctime)-15s - %(levelname)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

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

    # Create thumbnails
    srcfolder = os.path.join(app.instance_path, app.config.get("IMAGE_PATH"))
    destfolder = os.path.join(app.instance_path, app.config.get("THUMBNAIL_PATH"))
    for imgfile in os.listdir(srcfolder):
        src = os.path.join(srcfolder, imgfile)
        utils.save_thumbnail(src, destfolder)

    # Init session
    Session(app)

    # Init database
    from .models import DATABASE
    DATABASE.init(
        app.config.get("DB_NAME"),
        user=app.config.get("DB_USER"),
        password=app.config.get("DB_PASSWORD"),
        host=app.config.get("DB_HOST"),
        port=app.config.get("DB_PORT"))
    app.config["SQLDB"] = DATABASE

    # Create tables
    app.config.get("SQLDB").connect()
    usermodel.User.create_table()
    recipemodel.Recipe.create_table()
    tagmodel.TagCategory.create_table()
    tagmodel.Tag.create_table()
    tagmodel.RecipeTags.create_table()
    app.config.get("SQLDB").close()

    @app.before_request
    def before_request():
        """Connect to database before request."""
        app.config.get("SQLDB").connect()

    @app.after_request
    def after_request(response):
        """Close connection to database after request."""
        app.config.get("SQLDB").close()
        return response

    # Register blueprints
    from .views import general, authentication, parse_html, recipe_data, documentation
    app.register_blueprint(general.bp)
    app.register_blueprint(recipe_data.bp)
    app.register_blueprint(authentication.bp)
    app.register_blueprint(parse_html.bp)
    app.register_blueprint(documentation.bp)

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
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name):]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)
