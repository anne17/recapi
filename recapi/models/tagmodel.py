"""Tag table models."""

import peewee as pw
from playhouse.shortcuts import model_to_dict

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
    """Add entries for Tag and RecipeTags."""
    newTags = recipe_data.get("newTags", {})
    for tagname, category in newTags.items():
        tag = Tag(tagname=tagname, parent=TagCategory.get(TagCategory.categoryname == category))
        tag.save()

    tags = recipe_data.get("tags", [])
    for tagname in tags:
        recipetags = RecipeTags(recipeID=Recipe.get(Recipe.id == recipe_id), tagID=Tag.get(Tag.tagname == tagname))
        recipetags.save()


def get_tags_for_recipe(recipe_id):
    """Get a list of tags for a given recipe title."""
    tags = []
    entries = RecipeTags.select().join(Tag).where(RecipeTags.recipeID == recipe_id)
    # entries = RecipeTags.select().where(RecipeTags.recipeID == recipe_id)
    for entry in entries:
        e = model_to_dict(entry)
        tagname = e.get("tagID", {}).get("tagname", "")
        tags.append(tagname)
    return tags


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
