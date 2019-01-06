# import functools
import yaml
import markdown
from flask import jsonify

# from app import session


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
    return data


def md2html(data):
    """Convert markdown to html."""
    return markdown.markdown(data)


def get_recipe_by_title(recipies, title):
    """Find recipe with matching title in data base."""
    recipies = recipies.get("recipies")
    recipe = {}

    for r in recipies:
        if r.get("title") == title:
            recipe = r
            break

    if recipe:
        recipe["ingredients"] = md2html(recipe.get("ingredients", ""))
        recipe["contents"] = md2html(recipe.get("contents", ""))
    return recipe

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
