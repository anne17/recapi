import os

from flask import send_from_directory, request, session
from flask_restful import Resource

from app import app, api, Config
from user import User
import utils


class Hello(Resource):
    def get(self):
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        return utils.success_response("Hello!", routes=routes)


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
def handle_unauthorized(e):
    """Handle 401"""
    return utils.error_response("Unauthorized.")


@app.route('/pdf/<path:path>')
def send_pdf(path):
    """Serve PDF files."""
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "pdf")
    return send_from_directory(data_dir, path)


@app.route('/img/<path:path>')
def send_img(path):
    """Serve images."""
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "img")
    return send_from_directory(data_dir, path)


@app.route('/check_authentication', methods=['GET', 'POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        print("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", user=session.get("user"))
    else:
        print("Access denied")
        return utils.error_response("Access denied")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Check user credentials and log in if authorized."""
    if session.get("authorized"):
        return utils.success_response("User already authorized!")
    else:
        username = request.form["login"]
        password = request.form["password"]
        user = User(username)
        # print("User:", user.username, user.displayname, user.is_authenticated(password))

        if user.is_authenticated(password):
            session["authorized"] = True
            session["user"] = user.displayname
            print("User %s logged in successfully" % username)
            return utils.success_response("User %s logged in successfully!" % username,
                                          user=user.displayname)
        return utils.error_response("Invalid username or password!"), 401


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Remove session for current user."""
    session.clear()
    return utils.success_response("Logged out successfully")
