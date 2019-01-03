# import functools
import yaml
import markdown
from flask import jsonify

# from app import session


def load_data(yamlfile):
    """Load yaml file and return json object."""
    with open(yamlfile) as f:
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


def md2html(name="", portions=0, ingredients="", contents="", source=""):
    """Convert markdown recipe data to form with html."""
    data = {}
    data["name"] = name
    data["portions"] = str(portions)
    data["ingredients"] = markdown.markdown(ingredients)
    data["contents"] = markdown.markdown(contents)
    data["source"] = source

    # contents = markdown.markdown(contents)
    # ingredients = markdown.markdown(ingredients)
    # data = (
    #     f"<h1>{name}</h1>"
    #     f"{ingredients}"
    #     f"{contents}"
    # )
    return data

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
