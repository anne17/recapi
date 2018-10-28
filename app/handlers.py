import os

from flask import send_from_directory
from flask_restful import Resource
from flask_login import login_user, current_user

from app import app, api, Config
from user import User
import utils


class Hello(Resource):
    def get(self):
        return {"hello": "true"}

api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        return utils.load_data(Config.get("DATA", "database"))

api.add_resource(RecipeList, '/recipe-data')


@app.route('/pdf/<path:path>')
def send_pdf(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "pdf")
    return send_from_directory(data_dir, path)


@app.route('/img/<path:path>')
def send_img(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "img")
    return send_from_directory(data_dir, path)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     # form = LoginForm()
#     # if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#
#     user = User("anne", "apa")
#     a = login_user(user)
#     print("login user", a)
#     print("AUTHENTICATED:", user.is_authenticated())
#     # next = request.args.get('next')
#     # is_safe_url should check if the url is safe for redirects.
#     # See http://flask.pocoo.org/snippets/62/ for an example.
#     # if not is_safe_url(next):
#     #     return flask.abort(400)
#
#     return 'Success! User logged in!'
#     # return flask.redirect(next or flask.url_for('index'))
#     # return flask.render_template('login.html', form=form)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
@app.route('/login', methods=['GET', 'POST'])
def my_login():
    if current_user.is_authenticated:
        return 'User authenticated!'
    username = 'anne'
    password = 'apa'
    remember = True
    # user = User.query.filter_by(username=username).first()
    user = User(username, password)
    if not user.is_authenticated():
        print('Invalid username or password')
        return 'Invalid username or password'
    login_user(user, remember=remember)
    return 'User %s logged in' % username
    # return redirect(url_for('index'))
    # return render_template('login.html', title='Sign In', form=form)
