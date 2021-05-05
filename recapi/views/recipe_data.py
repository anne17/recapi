"""Routes related to recipe data."""

import os
import random
import traceback
from functools import reduce

import peewee as pw
from flask import Blueprint, current_app, request, session

from recapi import utils
from recapi.models import recipemodel, storedmodel, tagmodel
from recapi.models.usermodel import User

bp = Blueprint("recipe_data", __name__)


@bp.route("/recipe_data")
def recipe_data():
    """Return all available recipe data."""
    complete = True if request.args.get("complete", "false").lower() == "true" else False
    return get_recipe_data(published=True, complete_data=complete)


@bp.route("/recipe_suggestions")
@utils.gatekeeper()
def recipe_suggestions():
    """Return data for all unpublished recipes."""
    return get_recipe_data(published=False)


def get_recipe_data(published=False, complete_data=False):
    """Return published or unpublished recipe data."""
    try:
        Changed = User.alias()
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, storedmodel.Stored,
            pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.published == published
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
        ).group_by(
            recipemodel.Recipe.id)

        if complete_data:
            # Load in User table
            recipes = recipes.select(
                User, Changed, recipemodel.Recipe, storedmodel.Stored,
                pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
            ).switch(
                recipemodel.Recipe
            ).join(
                User, pw.JOIN.LEFT_OUTER, on=(User.id == recipemodel.Recipe.created_by).alias("a")
            ).switch(
                recipemodel.Recipe
            ).join(
                Changed, pw.JOIN.LEFT_OUTER, on=(Changed.id == recipemodel.Recipe.changed_by).alias("b"))

        data = recipemodel.get_recipes(recipes, complete_data=complete_data)
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
            filename = utils.make_random_filename(image_file, file_extension=".jpg")
            directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
            utils.save_upload_image(image_file, filename, directory)
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
    recipe_id = request.args.get("id")
    title = request.args.get("title")
    try:
        Changed = User.alias()
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, User, Changed, storedmodel.Stored,
            pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.id == recipe_id if recipe_id else
            recipemodel.Recipe.title == title
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
        ).switch(
            recipemodel.Recipe
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
        recipe = recipemodel.get_recipe(recipes[0])

        if convert:
            recipe = utils.recipe2html(recipe)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404

        return utils.success_response(msg="Data loaded", data=recipe)

    except IndexError:
        return utils.error_response(f"Could not find recipe with ID '{recipe_id}'"), 404

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
        data["published"] = False if data.get("published", True).lower() == "false" else True
        image_file = request.files.get("image")
        recipe_id = recipemodel.add_recipe(data)
        url = utils.make_url(data["title"], recipe_id)
        recipemodel.set_url(recipe_id, url)
        tagmodel.add_tags(data, recipe_id)
        storedmodel.add_recipe(recipe_id)
        save_image(data, recipe_id, image_file)
        return utils.success_response(msg="Recipe saved", url=url)

    except pw.IntegrityError:
        return utils.error_response("Recipe title already exists!"), 409

    except Exception as e:
        # Delete recipe data and image
        if recipe_id is not None:
            recipemodel.delete_recipe(recipe_id)
            storedmodel.delete_recipe(recipe_id)
        if filename is not None:
            img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
            filepath = os.path.join(img_path, filename)
            try:
                utils.remove_file(filepath)
            except Exception:
                current_app.logger.warning(f"Could not delete file: {filepath}")
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/edit_recipe", methods=["POST"])
@utils.gatekeeper()
def edit_recpie():
    """Edit a recipe that already exists in the data base."""
    try:
        data = request.form.to_dict()
        data = utils.deserialize(data)
        data["user"] = session.get("uid")  # Store info about which user edited last
        data["published"] = False if data.get("published", True).lower() == "false" else True
        url = utils.make_url(data["title"], data["id"])
        data["url"] = url
        image_file = request.files.get("image")
        if not image_file and not data["image"]:
            recipe = recipemodel.Recipe.get(recipemodel.Recipe.id == data["id"])
            if recipe.image:
                try:
                    utils.remove_file(utils.remove_file(os.path.join(current_app.config.get("IMAGE_PATH"), recipe.image)))
                except OSError:
                    current_app.logger.warning(traceback.format_exc())
        else:
            save_image(data, data["id"], image_file)
        recipemodel.edit_recipe(data["id"], data)
        tagmodel.add_tags(data, data["id"])
        return utils.success_response(msg="Recipe saved", url=url)

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
        url = utils.make_url(data["title"], recipe_id)
        recipemodel.set_url(recipe_id, url)
        tagmodel.add_tags(data, recipe_id)
        storedmodel.add_recipe(recipe_id)
        save_image(data, recipe_id, image_file)

        # Attempt to send email to admins
        try:
            msg = ("Hej kalufs-admin!\n\nEtt nytt receptförslag med titel \"{}\" har lämnats in av {}.\n"
                   "Logga in på https://kalufs.lol/recept för att granska och publicera receptet.\n\n"
                   "Vänliga hälsningar,\nkalufs.lol"
                   ).format(data.get("title"), data.get("suggester"))
            utils.send_mail(current_app.config.get("EMAIL_TO"), "Nytt receptförslag!", msg)
        except Exception:
            current_app.logger.error(traceback.format_exc())

        return utils.success_response(msg="Recipe saved", url=url)

    except pw.IntegrityError:
        return utils.error_response("Recipe title already exists!"), 409

    except Exception as e:
        # Delete recipe data and image
        if recipe_id is not None:
            recipemodel.delete_recipe(recipe_id)
            storedmodel.delete_recipe(recipe_id)
        if filename is not None:
            img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
            filepath = os.path.join(img_path, filename)
            try:
                utils.remove_file(filepath)
            except Exception:
                current_app.logger.warning(f"Could not delete file: {filepath}")
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


def save_image(data, recipe_id, image_file):
    """Save uploaded image in data base."""
    img_path = os.path.join(current_app.instance_path, current_app.config.get("IMAGE_PATH"))
    thumb_destfolder = os.path.join(current_app.instance_path, current_app.config.get("THUMBNAIL_PATH"))
    medium_destfolder = os.path.join(current_app.instance_path, current_app.config.get("MEDIUM_IMAGE_PATH"))

    if image_file:
        # Get filename and save image
        filename = utils.make_db_filename(image_file, id=str(recipe_id), file_extension=".jpg")
        utils.save_upload_image(image_file, filename, img_path)
        # Edit row to add image path
        data["image"] = filename
        recipemodel.set_image(recipe_id, data)
        # Save thumbnail
        src = os.path.join(img_path, filename)
        utils.save_downscaled(src, thumb_destfolder, thumbnail=True)
        utils.save_downscaled(src, medium_destfolder)

    # When recipe was parsed from external source, image is already uploaded
    elif data.get("image") and data.get("image", "").startswith("tmp"):
        filename = utils.make_db_filename(data["image"], id=str(recipe_id), file_extension=".jpg")
        # Get path to file and copy it from tmp to img folder
        src_directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
        src = os.path.join(src_directory, os.path.split(data["image"])[1])
        utils.copy_file(src, img_path, filename)
        # Edit row to add image file name
        data["image"] = filename
        recipemodel.set_image(recipe_id, data)
        # Save thumbnail
        src = os.path.join(img_path, filename)
        utils.save_downscaled(src, thumb_destfolder, thumbnail=True)
        utils.save_downscaled(src, medium_destfolder)


@bp.route("/delete_recipe")
@utils.gatekeeper()
def delete_recpie():
    """Remove recipe from data base."""
    try:
        recipe_id = request.args.get("id")
        recipe = recipemodel.Recipe.get(recipemodel.Recipe.id == recipe_id)
        if recipe.image:
            utils.remove_file(os.path.join(current_app.config.get("IMAGE_PATH"), recipe.image))
            utils.remove_file(os.path.join(current_app.config.get("THUMBNAIL_PATH"), recipe.image))
            utils.remove_file(os.path.join(current_app.config.get("MEDIUM_IMAGE_PATH"), recipe.image))
        tagmodel.delete_recipe(recipe_id)
        recipemodel.delete_recipe(recipe_id)
        storedmodel.delete_recipe(recipe_id)
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
            querytype = "tag"

            tagset = set(tag.split(","))
            tagstructure = tagmodel.get_tag_structure(simple=True)
            taggroups = []
            for cat in tagstructure:
                selected_tags = list(set(cat.get("tags")).intersection(tagset))
                if selected_tags:
                    taggroups.append(selected_tags)

            # Chain tags with OR within a category and with AND between categories
            and_expressions = []
            for taggroup in taggroups:
                or_expressions = [
                    pw.fn.FIND_IN_SET(tag, pw.fn.group_concat(tagmodel.Tag.tagname))
                    for tag in taggroup
                ]
                and_expressions.append(reduce(pw.operator.or_, or_expressions))
            expr = reduce(pw.operator.and_, and_expressions)

        elif user:
            # User search
            querytype = "user"
            expr = ((User.displayname == user) | recipemodel.Recipe.suggester.contains(user))

        else:
            # String search: seperate by whitespace and search in all relevant fields
            querytype = "q"
            if len(q) > 1 and q.startswith('"') and q.endswith('"'):
                searchitems = [q[1:-1]]
            else:
                searchitems = q.split(" ")
                searchitems = [i.rstrip(",") for i in searchitems]

            expr_list = [
                (
                    recipemodel.Recipe.title.contains(s)
                    | recipemodel.Recipe.contents.contains(s)
                    | recipemodel.Recipe.ingredients.contains(s)
                    | recipemodel.Recipe.source.contains(s)
                    | User.username.contains(s)
                    | pw.fn.FIND_IN_SET(s, pw.fn.group_concat(tagmodel.Tag.tagname))
                ) for s in searchitems
            ]
            expr = reduce(pw.operator.and_, expr_list)

        # Build query
        Changed = User.alias()
        query = recipemodel.Recipe.select(
            recipemodel.Recipe, User, Changed, storedmodel.Stored,
            pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
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
        ).having(expr)

        data = recipemodel.get_recipes(query)
        message = f"Query: {querytype}={q}"
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


@bp.route("/random")
def get_random_recipe():
    """Return one recipe at random from randomizer categories in config."""
    tags = current_app.config.get("RANDOM_TAGS", [])

    or_expressions = reduce(pw.operator.or_, [
        pw.fn.FIND_IN_SET(tag, pw.fn.group_concat(tagmodel.Tag.tagname))
        for tag in tags
    ])

    try:
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, storedmodel.Stored, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.published == True
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.RecipeTags, pw.JOIN.LEFT_OUTER, on=(tagmodel.RecipeTags.recipeID == recipemodel.Recipe.id)
        ).join(
            tagmodel.Tag, pw.JOIN.LEFT_OUTER, on=(tagmodel.Tag.id == tagmodel.RecipeTags.tagID)
        ).group_by(
            recipemodel.Recipe.id
        ).having(
            or_expressions
        )

        recipe = [random.choice(recipemodel.get_recipes(recipes))]
        return utils.success_response(msg="Got random recipe", data=recipe, hits=len(recipe))
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load data: {e}")


@bp.route("/toggle_stored", methods=["POST"])
@utils.gatekeeper()
def toggle_stored():
    """Toggle the 'stored' value of a recipe."""
    try:
        data = request.get_json()
        stored = data.get("stored", False)
        storedmodel.toggle_stored(data["id"], stored)
        if stored:
            return utils.success_response(msg="Recipe stored")
        else:
            return utils.success_response(msg="Recipe unstored")

    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/stored_recipes")
@utils.gatekeeper()
def stored_recipes():
    """Return data for all stored recipes."""
    try:
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, storedmodel.Stored, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
        ).where(
            storedmodel.Stored.stored == True
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


@bp.route("/toggle_needs_fix", methods=["POST"])
@utils.gatekeeper(allow_guest=True)
def toggle_needs_fix():
    """Toggle the 'needs_fix' value of a recipe."""
    try:
        data = request.form.to_dict()
        data = utils.deserialize(data)
        needs_fix = data.get("needs_fix", False)
        recipemodel.toggle_needs_fix(data["id"], needs_fix)
        if needs_fix:
            return utils.success_response(msg="Recipe marked as 'needs_fix'")
        else:
            return utils.success_response(msg="Recipe unmarked")

    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/needs_fix_recipes")
@utils.gatekeeper()
def needs_fix_recipes():
    """Return data for all recipes that need fixes."""
    try:
        recipes = recipemodel.Recipe.select(
            recipemodel.Recipe, storedmodel.Stored, pw.fn.group_concat(tagmodel.Tag.tagname).alias("taglist")
        ).where(
            recipemodel.Recipe.needs_fix == True
        ).join(
            storedmodel.Stored, pw.JOIN.LEFT_OUTER, on=(storedmodel.Stored.recipeID == recipemodel.Recipe.id)
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
