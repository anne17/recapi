"""Tag table models."""

import peewee as pw
# from playhouse.shortcuts import model_to_dict

from recapi.models import BaseModel
from recapi.models.recipemodel import Recipe


class TagCategory(BaseModel):
    """Tag category table (peewee model)."""

    categoryname = pw.CharField(unique=True, max_length="50")


class Tag(BaseModel):
    """Tag table (peewee model)."""

    tagname = pw.CharField(unique=True, max_length="50")
    parent = pw.ForeignKeyField(TagCategory, null=True)


class RecipeTags(BaseModel):
    """Table for tags per recipe (peewee model)."""

    recipeID = pw.ForeignKeyField(Recipe)
    tagID = pw.ForeignKeyField(Tag)


# def get_tag_structure():
#     """Get all categories, their tags and the number of recipies per tag."""
#     categories = TagCategory.select()
#     # Join with tags
#     data = []
#     # for category in categories:
#         # r = model_to_dict(category)
#         # data.append(r)
#     return data
