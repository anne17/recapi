"""Recipe database model."""

# from flask import current_app
import peewee as pw

# from recapi.models import BaseModel
from __init__ import BaseModel


class Recipe(BaseModel):
    """Recipe table (peewee model)."""

    title = pw.TextField()
    image = pw.TextField()
    source = pw.TextField()
    ingredients = pw.TextField()
    contents = pw.TextField()
    portions = pw.IntegerField()
    # tags = pw.ForeignKeyField()
    # created = pw.DateTimeField()
    # created_by = pw.ForeignKeyField()


# class Tag(BaseModel):
#     """Recipe tag table (peewee model)."""
#
#     tag = pw.TextField()
