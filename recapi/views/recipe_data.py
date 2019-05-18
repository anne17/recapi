"""Routes related to recipe data."""

import os
import traceback

from flask import request, current_app, Blueprint, session
import peewee as pw

from recapi import utils
from recapi.models import recipemodel, tagmodel
from recapi.models.usermodel import User

bp = Blueprint("recipe_data", __name__)


@bp.route("/recipe_data")
def recipe_data():
    """Return all available recipe data."""
    return get_recipe_data(published=True)


@bp.route("/recipe_suggestions")
@utils.gatekeeper()
def recipe_suggestions():
    """Return data for all unpublished recipes."""
    return get_recipe_data(published=False)


def get_recipe_data(published=False):
    """Return published or unpublished recipe data."""
    try:
        Changed = User.alias()
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, User, Changed, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.published == published
        ).join(
            User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
        ).switch(
            recipemodel.Recipe
        ).join(
            Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b")
        ).switch(
            recipemodel.Recipe
        ).join(
            tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
        ).group_by(recipemodel.Recipe.id)

        data = recipemodel.get_recipes(recipes)
        return utils.success_response(msg="Data loaded", data=data, hits=len(data))
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load data: {e}")


@bp.route("/preview_data", methods=['POST'])
def preview_data():
    """Generate recipe preview. Convert markdown data to html."""
    try:
        data = utils.recipe2html(request.form.to_dict())
        data = utils.deserialize(data)
        image_file = request.files.get("image")
        if image_file:
            filename = utils.make_random_filename(image_file)
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
    return get_recipe_from_db(convert=True)


@bp.route("/get_recipe")
def get_recipe():
    """Get data for one recipe."""
    return get_recipe_from_db()


def get_recipe_from_db(convert=False):
    """Get data for one recipe. Convert to html if convert=True."""
    try:
        title = request.args.get("title")

        Changed = User.alias()
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, User, Changed, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.title == title
        ).join(
            User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
        ).switch(
            recipemodel.Recipe
        ).join(
            Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b")
        ).switch(
            recipemodel.Recipe
        ).join(
            tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
        ).group_by(recipemodel.Recipe.id)
        recipe = recipemodel.get_recipes(recipes)[0]

        if convert:
            recipe = utils.recipe2html(recipe)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404

        return utils.success_response(msg="Data loaded", data=recipe)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load recipe: {e}"), 400


@bp.route("/add_recipe", methods=['POST'])
@utils.gatekeeper()
def add_recpie():
    """Add new recipe to the data base."""
    recipe_id = None
    filename = None
    try:
        data = request.form.to_dict()
        data = utils.deserialize(data)
        data["user"] = session.get("uid")
        image_file = request.files.get("image")
        recipe_id = recipemodel.add_recipe(data)
        tagmodel.add_tags(data, recipe_id)
        save_image(data, recipe_id, image_file)
        return utils.success_response(msg="Recipe saved")

    except pw.IntegrityError:
        return utils.error_response("Recipe title already exists!"), 409

    except Exception as e:
        # Delete recipe data and image
        if recipe_id is not None:
            recipemodel.delete_recipe(recipe_id)
        if filename is not None:
            img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
            filepath = os.path.join(img_path, filename)
            utils.remove_file(filepath)
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/edit_recipe", methods=["POST"])
@utils.gatekeeper()
def edit_recpie():
    """Edit a recipe that already exists in the data base."""
    try:
        data = request.form.to_dict()
        data = utils.deserialize(data)
        data["user"] = session.get("uid")  # Make visible which user edited last
        image_file = request.files.get("image")
        recipemodel.edit_recipe(data["id"], data)
        tagmodel.add_tags(data, data["id"])
        save_image(data, data["id"], image_file)
        return utils.success_response(msg="Recipe saved")

    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/suggest", methods=["POST"])
@utils.gatekeeper(allow_guest=True)
def suggest_recipe():
    """Save a recipe suggestion in the data base (published=False)."""
    recipe_id = None
    filename = None
    try:
        data = request.form.to_dict()
        data = utils.deserialize(data)
        data["user"] = session.get("uid")
        data["published"] = False
        image_file = request.files.get("image")
        recipe_id = recipemodel.add_recipe(data)
        tagmodel.add_tags(data, recipe_id)
        save_image(data, recipe_id, image_file)
        return utils.success_response(msg="Recipe saved")

    except pw.IntegrityError:
        return utils.error_response("Recipe title already exists!"), 409

    except Exception as e:
        # Delete recipe data and image
        if recipe_id is not None:
            recipemodel.delete_recipe(recipe_id)
        if filename is not None:
            img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
            filepath = os.path.join(img_path, filename)
            utils.remove_file(filepath)
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


def save_image(data, recipe_id, image_file):
    """Save uploaded image in data base."""
    if image_file:
        # Get filename and save image
        filename = utils.make_db_filename(image_file, id=str(recipe_id))
        img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
        utils.save_upload_file(image_file, filename, img_path)
        # Edit row to add image path
        data["image"] = "img/" + filename
        recipemodel.edit_recipe(recipe_id, data)
        tagmodel.add_tags(data, recipe_id)

    # When recipe was parsed from external source, image is already uploaded
    elif data.get("image") and data.get("image", "").startswith("tmp"):
        filename = utils.make_db_filename(data["image"], id=str(recipe_id))
        # Get path to file and copy it from tmp to img folder
        src_directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
        src = os.path.join(src_directory, os.path.split(data["image"])[1])
        img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
        utils.copy_file(src, img_path, filename)
        # Edit row to add image path
        data["image"] = "img/" + filename
        recipemodel.edit_recipe(recipe_id, data)
        tagmodel.add_tags(data, recipe_id)


@bp.route("/delete_recipe")
@utils.gatekeeper()
def delete_recpie():
    """Remove recipe from data base."""
    try:
        recipe_id = request.args.get("id")
        recipe = recipemodel.Recipe.get(recipemodel.Recipe.id == recipe_id)
        if recipe.image:
            utils.remove_file(recipe.image, relative=True)
        tagmodel.delete_recipe(recipe_id)
        recipemodel.delete_recipe(recipe_id)
        return utils.success_response(msg="Recipe removed")
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to remove recipe: {e}"), 400


@bp.route("/search")
def search():
    """Search recipe data base."""
    try:
        tag = request.args.get("tag")
        user = request.args.get("user")
        q = request.args.get("q")

        if tag:
            # Tag Search
            Changed = User.alias()
            query = recipemodel.Recipe.select(
                recipemodel.Recipe, User, Changed, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
            ).join(
                User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
            ).switch(
                recipemodel.Recipe
            ).join(
                Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b")
            ).switch(
                recipemodel.Recipe
            ).join(
                tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
            ).join(
                tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
            ).group_by(
                recipemodel.Recipe.id
            ).where(
                (recipemodel.Recipe.published == True)
            ).having(
                pw.fn.FIND_IN_SET(tag, pw.fn.group_concat(tagmodel.Tag.tagname))
            )
            data = recipemodel.get_recipes(query)
            message = f"Query: tag={tag}"

        elif user:
            # User search
            Changed = User.alias()
            query = recipemodel.Recipe.select(
                recipemodel.Recipe, User, Changed, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
            ).join(
                User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
            ).switch(
                recipemodel.Recipe
            ).join(
                Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b")
            ).switch(
                recipemodel.Recipe
            ).join(
                tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
            ).join(
                tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
            ).group_by(
                recipemodel.Recipe.id
            ).where(
                (recipemodel.Recipe.published == True)
                & (User.displayname == user)
            )
            data = recipemodel.get_recipes(query)
            message = f"Query: user={user}"

        else:
            # String search
            Changed = User.alias()
            query = recipemodel.Recipe.select(
                recipemodel.Recipe, User, Changed, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
            ).join(
                User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
            ).switch(
                recipemodel.Recipe
            ).join(
                Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b")
            ).switch(
                recipemodel.Recipe
            ).join(
                tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
            ).join(
                tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
            ).group_by(
                recipemodel.Recipe.id
            ).where(
                (recipemodel.Recipe.published == True)
            ).having(
                recipemodel.Recipe.contents.contains(q)
                | recipemodel.Recipe.ingredients.contains(q)
                | recipemodel.Recipe.source.contains(q)
                | User.username.contains(q)
                | pw.fn.FIND_IN_SET(q, pw.fn.group_concat(tagmodel.Tag.tagname))
            )

            data = recipemodel.get_recipes(query)
            message = f"Query: q={q}"

        return utils.success_response(msg=message, data=data, hits=len(data))
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Query failed: {e}"), 400


@bp.route("/get_tag_categories")
def get_tag_categories():
    """Return a list of tag categories."""
    cats = tagmodel.get_tag_categories()
    return utils.success_response(msg="", data=cats)


@bp.route("/get_tag_structure")
def get_tag_structure():
    cats = tagmodel.get_tag_structure()
    return utils.success_response(msg="", data=cats)


@bp.route("/get_tag_structure_simple")
def get_tag_structure_simple():
    cats = tagmodel.get_tag_structure(simple=True)
    return utils.success_response(msg="", data=cats)
