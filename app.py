# -*- coding: utf-8 -*-

import configparser
import yaml

from flask import Flask, send_from_directory, request
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_login import LoginManager, login_user

from user import User

app = Flask(__name__, static_url_path='')
CORS(app)
api = Api(app)
# login = LoginManager(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Read config
Config = configparser.ConfigParser()
Config.read("config.cfg")


class Hello(Resource):
    def get(self):
        return {"hello": "true"}


api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        return load_data(Config.get("DATA", "database"))


api.add_resource(RecipeList, '/recipe-data')


@app.route('/pdf/<path:path>')
def send_pdf(path):
    return send_from_directory('res/pdf', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('res/img', path)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    # form = LoginForm()
    # if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

    user = User("anne")
    login_user(user)

    print('Logged in successfully.')

    # next = request.args.get('next')
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    # if not is_safe_url(next):
    #     return flask.abort(400)

    return 'Success! User logged in!'
    # return flask.redirect(next or flask.url_for('index'))
    # return flask.render_template('login.html', form=form)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
# @app.route('/login', methods=['GET', 'POST'])
# def my_login():
#     if current_user.is_authenticated:
#         return 'User authenticated!'
#     username = 'anne'
#     password = '1234'
#     remember = True
#     user = User.query.filter_by(username=username).first()
#     if user is None or not user.check_password(password):
#         print('Invalid username or password')
#         return 'Invalid username or password'
#     login_user(user, remember=remember)
#     return 'User %s logged in' % username
#     # return redirect(url_for('index'))
#     # return render_template('login.html', title='Sign In', form=form)


def load_data(yamlfile):
    with open(yamlfile) as f:
        return yaml.load(f)


if __name__ == '__main__':
    app.run(
        debug=Config.getboolean("APP-SETTINGS", "debug_mode"),
        host=Config.get("APP-SETTINGS", "wsgi_host"),
        port=Config.get("APP-SETTINGS", "wsgi_port")
    )
