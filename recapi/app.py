# -*- coding: utf-8 -*-

import os

import configparser

from flask import Flask
from flask_session import Session
from flask_cors import CORS
from flask_restful import Api

# Init app
app = Flask(__name__)
api = Api(app)

# Enable CORS
CORS(app, supports_credentials=True)

# Read config
if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')) is False:
    print("Please copy config.default.cfg to config.cfg and add your settings!")
    print("Using default settings for now.")
    configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.default.cfg')
else:
    configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')

Config = configparser.ConfigParser()
Config.read(configfile)

# Init session
app.config.from_object(__name__)
app.config["SESSION_TYPE"] = Config.get("SESSION", "session_type")
app.config["SESSION_FILE_DIR"] = Config.get("SESSION", "file_dir")
app.secret_key = Config.get("SESSION", "secret_key")
Session(app)

# Load routes
from views import *


if __name__ == '__main__':
    app.run(
        debug=Config.getboolean("APP-SETTINGS", "debug_mode"),
        host=Config.get("APP-SETTINGS", "wsgi_host"),
        port=Config.get("APP-SETTINGS", "wsgi_port")
    )
