"""Collection of general routes."""

import os
import traceback

import yaml
from flask import send_from_directory, request, session, current_app, Blueprint, jsonify, render_template, url_for

from recapi.models import User
from recapi import utils

general = Blueprint("general", __name__)


@general.route("/routes")
def hello():
    """Say hi and show available routes."""
    routes = [str(rule) for rule in current_app.url_map.iter_rules()]
    return utils.success_response("Welcome to recAPI!", routes=routes)


@general.route("/api_spec")
def api_spec():
    """Return open API specification in json."""
    with open("static/recapi-oas.yaml", encoding="UTF-8") as f:
        return jsonify(yaml.load(f))


@general.route("/")
@general.route("/api_doc")
def api_doc():
    """Render HTML API documentation."""
    return render_template('apidoc.html',
                           title="recAPI documentation",
                           favicon=url_for("static", filename="favicon.ico"),
                           spec_url=url_for("general.api_spec")
                           )


@general.route("/recipe_data")
def recipe_data():
    """Return all available recipe data."""
    try:
        data = utils.load_data(current_app.config.get("DATABASE"))
        return utils.success_response(msg="Data loaded", data=data)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load data: {e}")


@general.errorhandler(404)
def page_not_found(e):
    """Handle 404."""
    return utils.error_response("Page not found.")


@general.errorhandler(401)
def handle_unauthorized(e):
    """Handle 401."""
    return utils.error_response("Unauthorized.")


@general.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    data_dir = os.path.join(current_app.config.get("MEDIA_PATH"))
    return send_from_directory(data_dir, path)


@general.route('/img/<path:path>')
def send_img(path):
    """Serve images."""
    data_dir = os.path.join(current_app.config.get("MEDIA_PATH"), "img")
    return send_from_directory(data_dir, path)


@general.route('/tmp/<path:path>')
def send_tmp(path):
    """Serve temporary files."""
    data_dir = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
    return send_from_directory(data_dir, path)


@general.route('/check_authentication', methods=['GET', 'POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        print("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", user=session.get("user"))
    else:
        return utils.error_response("Access denied")


@general.route('/login', methods=['GET', 'POST'])
def login():
    """Check user credentials and log in if authorized."""
    if session.get("authorized"):
        return utils.success_response("User already authorized!")
    else:
        username = request.form["login"]
        password = request.form["password"]
        user = User(username)
        current_app.logger.debug("User:", user.username, user.displayname, user.is_authenticated(password))

        if user.is_authenticated(password):
            session["authorized"] = True
            session["user"] = user.displayname
            session["uid"] = user.uid
            print("User %s logged in successfully" % username)
            return utils.success_response("User %s logged in successfully!" % username,
                                          user=user.displayname)
        return utils.error_response("Invalid username or password!"), 401


@general.route('/logout', methods=['GET', 'POST'])
def logout():
    """Remove session for current user."""
    session.clear()
    return utils.success_response("Logged out successfully")


@general.route("/preview_data", methods=['GET', 'POST'])
def preview_data():
    """Generate recipe preview. Convert markdown data to html."""
    try:
        data = utils.md2htmlform(request.form)
        image_file = request.files.get("image")
        if image_file:
            filename = utils.make_filename(image_file)
            directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
            utils.save_upload_file(image_file, filename, directory)
            data["image"] = "tmp/" + filename
        return utils.success_response(msg="Data converted", data=data)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to convert data: {e}")


@general.route("/view_recipe")
def view_recipe():
    """Generate view for one recipe. Convert markdown data to html."""
    try:
        title = request.args.get("title")
        recipies = utils.load_data(current_app.config.get("DATABASE"))
        recipe = utils.get_recipe_by_title(recipies, title, convert=True)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404
        return utils.success_response(msg="Data loaded", data=recipe)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load recipe: {e}"), 400


@general.route("/get_recipe")
def get_recipe():
    """Get data for one recipe."""
    try:
        title = request.args.get("title")
        recipies = utils.load_data(current_app.config.get("DATABASE"))
        recipe = utils.get_recipe_by_title(recipies, title)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404
        return utils.success_response(msg="Data loaded", data=recipe)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load recipe: {e}"), 400


@general.route("/clean_tmp_data")
def clean_tmp_data():
    """Clean temporary data like uploaded images."""
    password = request.args.get("password")
    if password != current_app.config.get("ADMIN_PASSWORD"):
        return utils.error_response("Failed to confirm password."), 500
    try:
        tmp_path = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
        data = utils.clean_tmp_folder(tmp_path)
        return utils.success_response(f"Successfully cleaned temporary data!",
                                      removed_files=data)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Cleanup failed: {e}"), 400
