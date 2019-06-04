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
    portions_text = pw.CharField(max_length="20")
    portions = pw.IntegerField()
    created_by = pw.ForeignKeyField(usermodel.User)
    created = pw.DateTimeField()
    changed_by = pw.ForeignKeyField(usermodel.User, null=True)
    changed = pw.DateTimeField(null=True)
    published = pw.BooleanField(default=True)
    suggestor = pw.CharField(max_length="100", null=True)


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
        suggestor=data.get("suggestor", None)
    )
    recipe.save()
    return recipe.id


def get_recipes(recipes):
    """Return all recipes in the database."""
    data = []
    for recipe in recipes:
        r = model_to_dict(recipe, recurse=False)
        # Add user data
        r["created_by"] = model_to_dict(recipe.a)
        r["created_by"].pop("password")
        r["changed_by"] = model_to_dict(recipe.b)
        r["changed_by"].pop("password")
        # Add tags
        r["tags"] = sorted(recipe.taglist.split(",")) if recipe.taglist else []
        data.append(r)
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
    recipe.portions_text = data.get("portions_text", "")
    recipe.portions = portion_str_to_number(data.get("portions_text", ""))
    recipe.changed_by = data.get("user")
    recipe.changed = datetime.datetime.now()
    recipe.published = data.get("published", True)
    recipe.suggestor = data.get("suggestor", None)
    recipe.save()


def delete_recipe(in_id):
    """Find recipe by id and remove from data base."""
    recipe = Recipe.get(Recipe.id == in_id)
    return recipe.delete_instance()


def portion_str_to_number(in_str):
    """Extract a numerical value from a portion_text field."""
    match = re.search(r"(\d+)", in_str)
    if match is not None:
        return int(match.group(1))
    return 0
