"""Routes related to recipe data."""

import os
import traceback

from flask import request, current_app, Blueprint

from recapi import utils

bp = Blueprint("recipe_data", __name__)


@bp.route("/recipe_data")
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


@bp.route("/preview_data", methods=['POST'])
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


@bp.route("/view_recipe")
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


@bp.route("/get_recipe")
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
