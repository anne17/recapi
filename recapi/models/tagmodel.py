"""Tag table models."""

import peewee as pw
# from playhouse.shortcuts import model_to_dict

from recapi.models import BaseModel
from recapi.models.recipemodel import Recipe


class TagCategory(BaseModel):
    """Tag category table (peewee model)."""

    categoryorder = pw.IntegerField()
    categoryname = pw.CharField(unique=True, max_length="50")


class Tag(BaseModel):
    """Tag table (peewee model)."""

    tagname = pw.CharField(unique=True, max_length="50")
    parent = pw.ForeignKeyField(TagCategory, null=True)


class RecipeTags(BaseModel):
    """Table for tags per recipe (peewee model)."""

    recipeID = pw.ForeignKeyField(Recipe)
    tagID = pw.ForeignKeyField(Tag)


def add_tags(recipe_data, recipe_id):
    """Add entries for Tag, TagCategory and RecipeTags."""
    tags = recipe_data.get("tags", [])
    newTags = recipe_data.get("newTags", [])


def get_tag_categories():
    """Get a list of tag categories."""
    categories = TagCategory.select()
    data = []
    for category in categories:
        catname = category.categoryname
        data.append(catname)
    return data


def get_tag_structure(simple=False):
    """Get all categories, their tags and the number of recipies per tag."""
    data = []
    categories = TagCategory.select()
    tags = Tag.select().join(TagCategory)
    for category in categories:
        catname = category.categoryname
        thesetags = tags.where(TagCategory.categoryname == catname)
        if simple:
            taglist = [t.tagname for t in thesetags]
        else:
            taglist = [{"name": t.tagname} for t in thesetags]
        # Todo: Get amount of recipies for earch tag
        thiscat = {
            "category": catname,
            "tags": taglist
        }
        data.append(thiscat)
    return data
