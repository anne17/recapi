"""Collection of utilities and auxiliaries."""

import functools
import os
import shutil
import time
import traceback
import uuid

from validator_collection import checkers
import markdown
from flask import jsonify, current_app, session
from werkzeug.datastructures import FileStorage


IMAGE_FORMATS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif"
}


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


def md2html(data):
    """Convert markdown to html."""
    return markdown.markdown(data)


def recipe2html(recipe):
    """Convert markdown recipe fields into html."""
    recipe["ingredients"] = md2html(recipe.get("ingredients", ""))
    recipe["contents"] = md2html(recipe.get("contents", ""))
    return recipe


def make_random_filename(infile, file_extension=None):
    """Generate a random file name with extension from infile."""
    if not file_extension:
        file_extension = get_file_extension(infile)
    filename = str(uuid.uuid1())
    return filename + file_extension


def make_db_filename(filename, id):
    """Generate a filename with id + file extension."""
    file_extension = get_file_extension(filename)
    return id + file_extension


def get_file_extension(file):
    """Get file extension for file (FileStorage or string with file name)."""
    if isinstance(file, FileStorage):
        return os.path.splitext(file.filename)[1]
    else:
        return os.path.splitext(file)[1]


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


def copy_file(src, destfolder, destfilename):
    """Copy file from src to destfolder with destfilename."""
    try:
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)
        dest = os.path.join(destfolder, destfilename)
        shutil.copyfile(src, dest)
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


def gatekeeper(function):
    """Stop unauthorized users. Use as decorator where authorization is needed."""
    @functools.wraps(function)  # Copy original function's information, needed by Flask
    def wrapper(*args, **kwargs):
        if not session.get("authorized"):
            return error_response("Access denied"), 401
        else:
            return function(*args, **kwargs)
    return wrapper
