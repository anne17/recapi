"""Tag table models."""

import peewee as pw

from recapi.models import BaseModel
from recapi.models.recipemodel import Recipe


class Stored(BaseModel):
    """Stored model for bookmarking recipes (peewee model)."""

    recipeID = pw.ForeignKeyField(Recipe)
    stored = pw.BooleanField(default=False)


def toggle_stored(recipe_id, stored_val):
    """Change the 'stored' value of a recipe."""
    stored_entry, _ = Stored.get_or_create(recipeID=recipe_id, defaults={"stored": False})
    stored_entry.stored = not stored_val
    stored_entry.save()


def add_recipe(recipe_id):
    """Add ID for new recipe to Stored table."""
    stored_entry = Stored(
        recipeID=recipe_id,
        stored=False
    )
    stored_entry.save()


def delete_recipe(recipe_id):
    """Remove 'stored' entry for a recipe."""
    return Stored.delete().where(Stored.recipeID == recipe_id).execute()
