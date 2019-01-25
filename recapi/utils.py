"""Collection of utilities and auxiliaries."""

# import functools
import os
import time
import traceback
import uuid

from validator_collection import checkers
import yaml
import markdown
from flask import jsonify, current_app


IMAGE_FORMATS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif"
}


def load_data(yamlfile):
    """Load yaml file and return json object."""
    with open(yamlfile, encoding="UTF-8") as f:
        return yaml.load(f)


def error_response(msg):
    """Create json error response."""
    return jsonify({
        "status": "error",
        "message": msg
    })


def success_response(msg, **kwargs):
    """Create json success response."""
    response = {
        "status": "success",
        "message": msg
    }
    for key, value in kwargs.items():
        response[key] = value
    return jsonify(response)


def md2htmlform(form):
    """Convert markdown recipe data to form with html."""
    data = {}
    data["title"] = form.get("title")
    data["portions"] = form.get("portions")
    data["ingredients"] = md2html(form.get("ingredients"))
    data["contents"] = md2html(form.get("contents"))
    data["source"] = form.get("source")
    data["image"] = form.get("image")
    return data


def md2html(data):
    """Convert markdown to html."""
    return markdown.markdown(data)


def get_recipe_by_title(recipies, title, convert=False):
    """Find recipe with matching title in data base."""
    recipies = recipies.get("recipies")
    recipe = {}

    for r in recipies:
        if r.get("title") == title:
            recipe = r
            break

    if convert and recipe:
        recipe["ingredients"] = md2html(recipe.get("ingredients", ""))
        recipe["contents"] = md2html(recipe.get("contents", ""))
    return recipe


def make_filename(infile, file_extension=None):
    """Generate a random file name with extension from infile."""
    if not file_extension:
        _filename, file_extension = os.path.splitext(infile.filename)
    filename = str(uuid.uuid1())
    return filename + file_extension


def save_upload_file(file, filename, upload_folder):
    """Save uploaded file."""
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file.save(os.path.join(upload_folder, filename))
        return True
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        raise e


def save_upload_data(data, filename, upload_folder):
    """Save upload data to file."""
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        with open(os.path.join(upload_folder, filename), 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        raise e


def valid_url(url):
    """Check if input is a valid url."""
    return checkers.is_url(url)


def clean_tmp_folder(tmp_folder, timeout=604800):
    """Delete data in temp folder that has lived longer than the timeout (1 week)."""
    current_time = time.time()
    removed = []
    for filename in os.listdir(tmp_folder):
        filepath = os.path.join(tmp_folder, filename)
        mod_date = os.path.getmtime(filepath)
        old = True if current_time - mod_date > timeout else False
        if old:
            remove_file(filepath)
            removed.append(filename)
    return removed


def remove_file(filepath):
    """Delete file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        raise e


# def gatekeeper(function):
#     """Stop unauthorized users. Use as decorator where authorization is needed."""
#     @functools.wraps(function)  # Copy original function's information, needed by Flask
#     def wrapper(*args, **kwargs):
#         if not session.get("authorized"):
#             return jsonify({"error": "Access denied"})
#         else:
#             return function(*args, **kwargs)
#
#     return wrapper

# Example:
# @app.route("/coolfunc")
# @gatekeeper
# def coolfunc():
