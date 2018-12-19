import os
import configparser
from flask import Flask
from flask_session import Session
from flask_cors import CORS
# from flask_restful import Api

# api = Api()


def create_app():
    """https://github.com/pallets/flask/blob/master/examples/tutorial/flaskr/__init__.py"""
    app = Flask(__name__)
    # api.init_app(app)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Read config
    if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')) is False:
        print("Please copy config.default.cfg to config.cfg and add your settings!")
        print("Using default settings for now.")
        configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.default.cfg')
        # configfile = "config.default.cfg"
    else:
        configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')
        # configfile = "config.cfg"

    # Config = configparser.ConfigParser()
    # Config.read(configfile)
    app.config.from_pyfile(configfile)  # ???

    # Init session
    # app.config.from_object(__name__)
    # app.config["SESSION_TYPE"] = Config.get("SESSION", "session_type")
    # app.config["SESSION_FILE_DIR"] = Config.get("SESSION", "file_dir")
    # app.secret_key = Config.get("SESSION", "secret_key")
    Session(app)

    # from yourapplication.model import db
    # db.init_app(app)
    #
    # from yourapplication.views.admin import admin
    # from yourapplication.views.frontend import frontend
    # app.register_blueprint(admin)
    # app.register_blueprint(frontend)

    from . import views
    app.register_blueprint(views.general)

    return app
