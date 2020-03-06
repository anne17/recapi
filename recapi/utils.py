"""Collection of utilities and auxiliaries."""

import functools
import json
import os
import shutil
import time
import traceback
import uuid

import bleach
from bleach_whitelist import markdown_tags, markdown_attrs
from PIL import Image
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
    html = bleach.clean(markdown.markdown(data), markdown_tags, markdown_attrs)
    return html


def recipe2html(recipe):
    """Convert markdown recipe fields into html."""
    recipe["ingredients"] = md2html(recipe.get("ingredients", ""))
    recipe["contents"] = md2html(recipe.get("contents", ""))
    return recipe


def deserialize(recipe):
    """Deserialise JSON strings."""
    recipe["tags"] = json.loads(recipe.get("tags", []))
    recipe["newTags"] = json.loads(recipe.get("newTags", {}))
    return recipe


def make_random_filename(infile, file_extension=None):
    """Generate a random file name with extension from infile."""
    if not file_extension:
        file_extension = get_file_extension(infile)
    filename = str(uuid.uuid1())
    return filename + file_extension.lower()


def make_db_filename(filename, id, file_extension=None):
    """Generate a filename with id + file extension."""
    if not file_extension:
        file_extension = get_file_extension(filename)
    return id + file_extension.lower()


def get_file_extension(file):
    """Get file extension for file (FileStorage or string with file name)."""
    if isinstance(file, FileStorage):
        return os.path.splitext(file.filename)[1]
    else:
        return os.path.splitext(file)[1]


def save_upload_image(file, filename, upload_folder):
    """Save uploaded image and convert to jpg."""
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        imageobj = Image.open(file)
        imageobj = imageobj.convert('RGB')
        imageobj.save(os.path.join(upload_folder, filename), format="jpeg")
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


def save_downscaled(src, destfolder, thumbnail=False, overwrite=True):
    """Create a downscaled image from src and save it in destfolder."""
    try:
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)

        filename = os.path.basename(src)
        file, ext = os.path.splitext(filename)
        outpath = os.path.join(destfolder, file + ".jpg")

        # Do not downscale image if it already exists
        if (overwrite is False) and os.path.exists(destfolder):
            return

        if thumbnail:
            size = 512, 512
        else:
            size = 1110, 1110
        im = Image.open(src)
        im.thumbnail(size)
        im.save(outpath, "JPEG")
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


def remove_file(filepath, relative=False):
    """Delete file."""
    try:
        if relative:
            # Find absolute path for filepath
            head, tail = os.path.split(filepath)
            if head.startswith("img"):
                image_dir = os.path.join(current_app.instance_path,
                                         current_app.config.get("IMAGE_PATH"))
                filepath = os.path.join(image_dir, tail)
            elif head.startswith("tmp"):
                tmp_path = os.path.join(current_app.instance_path,
                                        current_app.config.get("TMP_DIR"))
                filepath = os.path.join(tmp_path, tail)
            else:
                raise OSError("Could not find absolute path for file %s" % filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        current_app.logger.error("Could not delete file: %s", traceback.format_exc())
        raise e


def gatekeeper(allow_guest=False):
    """Stop unauthorized users. Use as decorator where authorization is needed."""
    def decorator(function):
        @functools.wraps(function)  # Copy original function's information, needed by Flask
        def wrapper(*args, **kwargs):
            if not session.get("authorized") or (not session.get("admin") and not allow_guest):
                return error_response("Access denied"), 401
            else:
                return function(*args, **kwargs)
        return wrapper
    return decorator
