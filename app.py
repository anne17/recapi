# import configparser
import yaml

from flask import Flask, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_login import LoginManager

app = Flask(__name__, static_url_path='')
CORS(app)
api = Api(app)
login = LoginManager(app)

# Read config
app.config.from_pyfile("app_conf.ini")

# import os
# Config = configparser.ConfigParser()
# Config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_conf.ini'))
# Config.read("app_conf.ini")


class Hello(Resource):
    def get(self):
        return {"hello": "true"}

api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        # print(app.config)
        # print(Config.sections())
        # print(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_conf.ini'))
        # return Config.sections()
        # return load_data(Config["DEFAULT"]["DATABASE"])
        return load_data("data/database.yaml")

api.add_resource(RecipeList, '/recipe-data')


@app.route('/pdf/<path:path>')
def send_pdf(path):
    return send_from_directory('res/pdf', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('res/img', path)

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         login_user(user)
#
#         flask.flash('Logged in successfully.')
#
#         next = flask.request.args.get('next')
#         # is_safe_url should check if the url is safe for redirects.
#         # See http://flask.pocoo.org/snippets/62/ for an example.
#         if not is_safe_url(next):
#             return flask.abort(400)
#
#         return flask.redirect(next or flask.url_for('index'))
#     return flask.render_template('login.html', form=form)


def load_data(yamlfile):
    with open(yamlfile) as f:
        return yaml.load(f)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9005)
