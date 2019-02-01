"""Collection of general routes."""

import os
import traceback

import yaml
from flask import send_from_directory, request, session, current_app, Blueprint, jsonify, render_template, url_for, redirect

from recapi.models import User
from recapi import utils

general = Blueprint("general", __name__)


@general.route("/routes")
def hello():
    """Say hi and show available routes."""
    routes = [str(rule) for rule in current_app.url_map.iter_rules()]
    return utils.success_response("Listing available routes", routes=routes)


@general.route("/api_spec")
def api_spec():
    """Return open API specification in json."""
    spec_file = os.path.join(current_app.static_folder, "recapi-oas.yaml")
    with open(spec_file, encoding="UTF-8") as f:
        return jsonify(yaml.load(f))


@general.route("/")
def base_route():
    """Redirect to /api_doc."""
    return redirect(url_for('general.api_doc', _external=True))


@general.route("/api_doc")
def api_doc():
    """Render HTML API documentation."""
    current_app.logger.info("URL: %s", url_for("general.api_spec", _external=True))
    return render_template('apidoc.html',
                           title="recAPI documentation",
                           favicon=url_for("static", filename="favicon.ico", _external=True),
                           spec_url=url_for("general.api_spec", _external=True)
                           )


@general.route("/recipe_data")
def recipe_data():
    """Return all available recipe data."""
    try:
        data_path = os.path.join(current_app.config.get("ROOT_PATH"),
                                 current_app.config.get("DATABASE"))
        data = utils.load_data(data_path)
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


@general.route('/img/<filename>')
def send_img(filename):
    """Serve images."""
    image_dir = os.path.join(current_app.config.get("ROOT_PATH"),
                             current_app.config.get("IMAGE_PATH"))
    return send_from_directory(image_dir, filename)


@general.route('/tmp/<filename>')
def send_tmp(filename):
    """Serve temporary files."""
    data_dir = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
    return send_from_directory(data_dir, filename)


@general.route('/check_authentication', methods=['POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        current_app.logger.debug("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", authenticated=True, user=session.get("user"))
    else:
        return utils.success_response("Access denied", authenticated=False)


@general.route('/login', methods=['POST'])
def login():
    """Check user credentials and log in if authorized."""
    if session.get("authorized"):
        return utils.success_response("User already authorized!")
    else:
        username = request.get_json().get("login")
        password = request.get_json().get("password")
        # username = request.form["login"]
        # password = request.form["password"]
        user = User(username)
        current_app.logger.debug(f"User: {user.username}, {user.displayname}, {user.is_authenticated(password)}")

        if user.is_authenticated(password):
            session["authorized"] = True
            session["user"] = user.displayname
            session["uid"] = user.uid
            current_app.logger.debug("User %s logged in successfully" % username)
            return utils.success_response("User %s logged in successfully!" % username,
                                          user=user.displayname)
        return utils.error_response("Invalid username or password!"), 401


@general.route('/logout', methods=['POST'])
def logout():
    """Remove session for current user."""
    session.clear()
    return utils.success_response("Logged out successfully")


@general.route("/preview_data", methods=['POST'])
def preview_data():
    """Generate recipe preview. Convert markdown data to html."""
    try:
        data = utils.md2htmlform(request.get_json())
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
