import os

from flask import send_from_directory, request
from flask_restful import Resource

from app import app, api, Config, auth
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


@auth.verify_password
# https://github.com/flask-restful/flask-restful/issues/492
# https://flask-httpauth.readthedocs.io/en/latest/
# Set @auth.login_required on authorized routes
def verify_pw(username, password):
    user = User(username)
    return user.is_authenticated(password)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form["login"]
    password = request.form["password"]
    user = User(username)
    # print("User:", user.username, user.displayname, user.is_authenticated(password))

    if user.is_authenticated(password):
        print("user %s logged in successfully" % username)
        return utils.success_response("User %s logged in successfully!\n" % username,
                                      user=user.displayname)
    return utils.error_response("Invalid username or password!")
