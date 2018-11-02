import os

from flask import send_from_directory, request
from flask_restful import Resource
from flask_login import login_user, current_user, login_required, logout_user

from app import app, api, Config
from user import User
import utils


class Hello(Resource):
    def get(self):
        return utils.success_response("Hello!")

api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        return utils.load_data(Config.get("DATA", "database"))

api.add_resource(RecipeList, '/recipe-data')


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404"""
    return utils.error_response("Page not found.")

@app.errorhandler(401)
def page_not_found(e):
    """Handle 401"""
    return utils.error_response("Unauthorized.")

@app.route('/pdf/<path:path>')
def send_pdf(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "pdf")
    return send_from_directory(data_dir, path)


@app.route('/img/<path:path>')
def send_img(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "img")
    return send_from_directory(data_dir, path)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
# https://github.com/maxcountryman/flask-login
@app.route('/login', methods=['GET', 'POST'])
def my_login():
    if current_user.is_authenticated:
        print("Current user is already authenticated.")
        return utils.success_response("User %s is already authenticated!\n" % current_user.username,
                                      current_user.displayname)

    username = request.form["login"]
    password = request.form["password"]
    remember = request.form["remember"]
    user = User()
    user.username = username
    if not user.is_authenticated(password):
        return utils.error_response("Invalid username or password!")
    login_user(user, remember=remember)
    # next = request.args.get('next')
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    # if not is_safe_url(next):
    #     return flask.abort(400)
    print("user %s logged in successfully" % username)
    return utils.success_response("User %s logged in successfully!\n" % username,
                                  user=user.displayname)


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    """Handle logout."""
    print("Attempting to logout")
    logout_user()
    print("Still attempting to logout")
    return utils.success_response("User logged out.")
