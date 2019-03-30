"""Collection of general routes."""

import os
import traceback

from flask import send_from_directory, request, current_app, Blueprint

from recapi import utils

bp = Blueprint("general", __name__)


@bp.route("/routes")
def hello():
    """Say hi and show available routes."""
    routes = [str(rule) for rule in current_app.url_map.iter_rules()]
    return utils.success_response("Listing available routes", routes=routes)


@bp.errorhandler(404)
def page_not_found(e):
    """Handle 404."""
    return utils.error_response("Page not found.")


@bp.errorhandler(401)
def handle_unauthorized(e):
    """Handle 401."""
    return utils.error_response("Unauthorized.")


@bp.route('/defaultimg')
def send_default_img():
    return current_app.send_static_file("default.png")


@bp.route('/img/<filename>')
def send_img(filename):
    """Serve images."""
    image_dir = os.path.join(current_app.config.get("ROOT_PATH"),
                             current_app.config.get("IMAGE_PATH"))
    return send_from_directory(image_dir, filename)


@bp.route('/tmp/<filename>')
def send_tmp(filename):
    """Serve temporary files."""
    data_dir = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
    return send_from_directory(data_dir, filename)


@bp.route("/clean_tmp_data")
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
