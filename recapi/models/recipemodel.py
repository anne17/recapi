"""Recipe database model."""

import datetime
import re

import peewee as pw
from playhouse.shortcuts import model_to_dict

from recapi.models import BaseModel, usermodel


class Recipe(BaseModel):
    """Recipe table (peewee model)."""

    title = pw.CharField(unique=True, max_length="100")
    image = pw.TextField()
    source = pw.TextField()
    ingredients = pw.TextField()
    contents = pw.TextField()
    portions_text = pw.CharField(max_length="100")
    portions = pw.IntegerField()
    created_by = pw.ForeignKeyField(usermodel.User)
    created = pw.DateTimeField()
    changed_by = pw.ForeignKeyField(usermodel.User, null=True)
    changed = pw.DateTimeField(null=True)
    published = pw.BooleanField(default=True)
    suggester = pw.CharField(max_length="100", null=True)
    needs_fix = pw.BooleanField(default=False)
    needs_fix_text = pw.TextField()


def add_recipe(data):
    """Add recipe to database."""
    portions = portion_str_to_number(data.get("portions_text", ""))
    recipe = Recipe(
        title=data.get("title"),
        image=data.get("image", ""),
        source=data.get("source", ""),
        ingredients=data.get("ingredients", ""),
        contents=data.get("contents", ""),
        portions_text=data.get("portions_text", ""),
        portions=portions,
        created=datetime.datetime.now(),
        created_by=data.get("user"),
        changed_by=None,
        changed=None,
        published=data.get("published", True),
        suggester=data.get("suggester", None),
        needs_fix=data.get("needs_fix", False),
        needs_fix_text=data.get("needs_fix_text", "")
    )
    recipe.save()
    return recipe.id


def get_recipe(recipe):
    """Return data for one recipe."""
    r = model_to_dict(recipe, recurse=False)
    # Add user data
    r["created_by"] = model_to_dict(recipe.a)
    r["created_by"].pop("password")
    if hasattr(recipe, "b"):
        r["changed_by"] = model_to_dict(recipe.b)
    else:
        r["changed_by"] = model_to_dict(usermodel.User())
    r["changed_by"].pop("password")
    # Add tags
    r["tags"] = sorted(recipe.taglist.split(",")) if recipe.taglist else []
    # Add stored value
    r["stored"] = recipe.stored.stored
    return r


def get_recipes(recipes, complete_data=False):
    """Return list of recipes."""
    data = []
    for recipe in recipes:
        r = model_to_dict(recipe, recurse=False)

        # Add tags
        r["tags"] = sorted(recipe.taglist.split(",")) if recipe.taglist else []
        data.append(r)

        # Add stored values
        r["stored"] = recipe.stored.stored

        if complete_data:
            # Add user data
            r["created_by"] = model_to_dict(recipe.a)
            r["created_by"].pop("password")
            if hasattr(recipe, "b"):
                r["changed_by"] = model_to_dict(recipe.b)
            else:
                r["changed_by"] = model_to_dict(usermodel.User())
            r["changed_by"].pop("password")

        else:
            # Remove data not needed in listing
            r.pop("contents")
            r.pop("ingredients")
            r.pop("portions")
            r.pop("portions_text")
            r.pop("source")
            r.pop("suggester")
            r.pop("created")
            r.pop("created_by")
            r.pop("changed")
            r.pop("changed_by")
            r.pop("needs_fix_text")

    # Reverse list to display the newest recipe first
    data.reverse()
    return data


def edit_recipe(in_id, data):
    """Override data of an existing recipe. Find recipe by ID."""
    recipe = Recipe.get(Recipe.id == in_id)
    recipe.title = data.get("title")
    recipe.image = data.get("image", "")
    recipe.source = data.get("source", "")
    recipe.ingredients = data.get("ingredients", "")
    recipe.contents = data.get("contents", "")
    recipe.portions_text = portion_text_extend(data.get("portions_text", ""))
    recipe.portions = portion_str_to_number(data.get("portions_text", ""))
    recipe.changed_by = data.get("user")
    recipe.changed = datetime.datetime.now()
    recipe.published = data.get("published", True)
    recipe.suggester = data.get("suggester", None)
    recipe.save()


def toggle_needs_fix(in_id, needs_fix):
    """Change the 'needs_fix' value of a recipe."""
    recipe = Recipe.get(Recipe.id == in_id)
    recipe.needs_fix = needs_fix
    if needs_fix == False:
        recipe.needs_fix_text = ""
    recipe.save()


def set_image(in_id, data):
    """Set image of recipe without changing any other data."""
    recipe = Recipe.get(Recipe.id == in_id)
    recipe.image = data.get("image", "")
    recipe.save()


def delete_recipe(in_id):
    """Find recipe by id and remove from data base."""
    recipe = Recipe.get(Recipe.id == in_id)
    return recipe.delete_instance()


def portion_text_extend(in_str):
    """Add 'portioner' if string contains numbers only."""
    if re.fullmatch(in_str, r"\d+"):
        return in_str + " portioner"
    return in_str


def portion_str_to_number(in_str):
    """Extract a numerical value from a portion_text field."""
    match = re.search(r"(\d+)", in_str)
    if match is not None:
        return int(match.group(1))
    return 0
