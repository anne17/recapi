# -*- coding: utf-8 -*-

import os

import configparser

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_login import LoginManager

# Init app
app = Flask(__name__, static_url_path='')
api = Api(app)

# Enable CORS
CORS(app)

# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Read config
if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')) is False:
    print("Please copy config.default.cfg to config.cfg and add your settings!")
    print("Using default settings for now.")
    configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.default.cfg')
else:
    configfile = os.path.join(os.path.dirname(app.config.root_path), 'config.cfg')

Config = configparser.ConfigParser()
Config.read(configfile)

app.secret_key = Config.get("SESSION", "secret_key")

# Load paths
from handlers import *


if __name__ == '__main__':
    app.run(
        debug=Config.getboolean("APP-SETTINGS", "debug_mode"),
        host=Config.get("APP-SETTINGS", "wsgi_host"),
        port=Config.get("APP-SETTINGS", "wsgi_port")
    )
