"""Recipe database model."""

import datetime

import peewee as pw
from playhouse.shortcuts import model_to_dict, dict_to_model

from recapi.models import BaseModel, usermodel


class Recipe(BaseModel):
    """Recipe table (peewee model)."""

    title = pw.CharField(unique=True, max_length="100")
    image = pw.TextField()
    source = pw.TextField()
    ingredients = pw.TextField()
    contents = pw.TextField()
    portions = pw.IntegerField()
    created_by = pw.ForeignKeyField(usermodel.User)
    created = pw.DateTimeField()
    # tags = pw.ForeignKeyField()


def add_recipe(data):
    """Add recipe to database."""
    recipe = Recipe(
        title=data.get("title"),
        image=data.get("image", ""),
        source=data.get("source", ""),
        ingredients=data.get("ingredients", ""),
        contents=data.get("contents", ""),
        portions=data.get("portions", 0),
        created=datetime.datetime.now(),
        created_by=data.get("user")
    )
    recipe.save()
    return recipe.id


def get_recipe(in_title):
    """Retrieve a recipe by title."""
    return model_to_dict(Recipe.get(Recipe.title == in_title))


def get_all_recipies():
    """Return all recipies in the database."""
    recipies = Recipe.select()
    data = []
    for recipe in recipies:
        r = model_to_dict(recipe)
        # Remove password hash
        r.get("created_by", {}).pop("password")
        data.append(r)
    return data


def edit_recipe(in_id, data):
    """Override data of an existing recipe. Find recipe by ID."""
    recipe = Recipe.get(Recipe.id == in_id)
    recipe.title = data.get("title")
    recipe.image = data.get("image", "")
    recipe.source = data.get("source", "")
    recipe.ingredients = data.get("ingredients", "")
    recipe.contents = data.get("contents", "")
    recipe.portions = data.get("portions", 0)
    recipe.save()


def delete_recipe(in_id):
    """Find recipe by id and remove from data base."""
    recipe = Recipe.get(Recipe.id == in_id)
    return recipe.delete_instance()
