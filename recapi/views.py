import os

from flask import send_from_directory, request, session, current_app, Blueprint

# from recapi import api
from recapi.models import User
from recapi import utils

general = Blueprint("general", __name__)


@general.route("/")
def hello():
    routes = [str(rule) for rule in current_app.url_map.iter_rules()]
    return utils.success_response("Hello!", routes=routes)


@general.route("/recipe-data")
def recipe_data():
    try:
        data = utils.load_data(current_app.config.get("DATABASE"))
        return utils.success_response(msg="Data loaded", data=data)
    except Exception as e:
        # logging.error(traceback.format_exc())
        return utils.error_response(f"Failed to load data: {e}")


@general.errorhandler(404)
def page_not_found(e):
    """Handle 404"""
    return utils.error_response("Page not found.")


@general.errorhandler(401)
def handle_unauthorized(e):
    """Handle 401"""
    return utils.error_response("Unauthorized.")


@general.route('/pdf/<path:path>')
def send_pdf(path):
    """Serve PDF files."""
    data_dir = os.path.join(current_app.config.get("MEDIA_DIR"), "pdf")
    return send_from_directory(data_dir, path)


@general.route('/img/<path:path>')
def send_img(path):
    """Serve images."""
    data_dir = os.path.join(current_app.config.get("MEDIA_DIR"), "img")
    return send_from_directory(data_dir, path)


@general.route('/tmp/<path:path>')
def send_tmp(path):
    """Serve temporary files."""
    data_dir = os.path.join(current_app.config.get("TMP_DIR"))
    return send_from_directory(data_dir, path)


@general.route('/check_authentication', methods=['GET', 'POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        print("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", user=session.get("user"))
    else:
        print("Access denied")
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
        # print("User:", user.username, user.displayname, user.is_authenticated(password))

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
def preview():
    """Generate recipe preview. Convert markdown data to html."""
    try:
        data = utils.md2htmlform(request.form)
        image_file = request.files.get("image")
        if image_file:
            filename = utils.make_filename(image_file)
            utils.save_upload_file(image_file, filename, current_app.config.get("TMP_DIR"))
            data["image"] = filename
        return utils.success_response(msg="Data converted", data=data)
    except Exception as e:
        # logging.error(traceback.format_exc())
        return utils.error_response(f"Failed to convert data: {e}")


@general.route("/view_recipe")
def view():
    """Generate view for one recipe. Convert markdown data to html."""
    try:
        title = request.args.get("title")
        recipies = utils.load_data(current_app.config.get("DATABASE"))
        recipe = utils.get_recipe_by_title(recipies, title)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404
        return utils.success_response(msg="Data loaded", data=recipe)
    except Exception as e:
        # logging.error(traceback.format_exc())
        return utils.error_response(f"Failed to load recipe: {e}"), 400
