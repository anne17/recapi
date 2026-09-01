"""Tag table models."""

import peewee as pw

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


def _normalize_tags(tags):
    """Normalize a tag list and drop duplicates while preserving order."""
    normalized_tags = []
    seen = set()
    if not isinstance(tags, list):
        return normalized_tags

    for tagname in tags:
        if not isinstance(tagname, str):
            continue
        normalized = tagname.lower().strip()
        if normalized and normalized not in seen:
            normalized_tags.append(normalized)
            seen.add(normalized)
    return normalized_tags


def add_tags(recipe_data, recipe_id):
    """Add entries for Tag and RecipeTags and delete removed tags."""
    newTags = recipe_data.get("newTags") or {}
    if isinstance(newTags, dict):
        for tagname, category in newTags.items():
            normalized = tagname.lower().strip()
            if not normalized:
                continue
            Tag.get_or_create(
                tagname=normalized,
                defaults={"parent": TagCategory.get(TagCategory.categoryname == category)}
            )

    recipe = Recipe.get(Recipe.id == recipe_id)
    requested_tags = _normalize_tags(recipe_data.get("tags") or [])

    # Load current relations and collapse any duplicate rows for this recipe.
    existing_tags_rows = (
        RecipeTags
        .select(RecipeTags, Tag)
        .join(Tag, pw.JOIN.LEFT_OUTER)
        .where(RecipeTags.recipeID == recipe_id)
        .order_by(RecipeTags.id)
    )
    existing_tags = {}
    for row in existing_tags_rows:
        tagname = row.tagID.tagname.lower().strip()
        existing_tags.setdefault(tagname, []).append(row)

    for duplicate_rows in existing_tags.values():
        for duplicate_row in duplicate_rows[1:]:
            duplicate_row.delete_instance()

    existing_tag_names = set(existing_tags)

    # Add tags if they don't exist already.
    for tagname in requested_tags:
        if tagname not in existing_tag_names:
            RecipeTags.get_or_create(
                recipeID=recipe,
                tagID=Tag.get(Tag.tagname == tagname)
            )

    # Delete removed tags.
    requested_tag_names = set(requested_tags)
    for tagname, rows in existing_tags.items():
        if tagname not in requested_tag_names:
            rows[0].delete_instance()
            # Remove this tag from Tag table if no other recipe uses it
            delete_abandoned_tag(in_tagname=tagname)


def delete_recipe(recipe_id):
    """Remove all records belonging to a recipe."""
    recipetags = RecipeTags.select().where(RecipeTags.recipeID == recipe_id)
    for record in recipetags:
        tagID = record.tagID
        record.delete_instance()
        delete_abandoned_tag(tag_instance=Tag.get(Tag.id == tagID))


def delete_abandoned_tag(in_tagname="", tag_instance=None):
    """Remove tag from database (by name or peewee instance) if there are no references of it left in RecipeTags."""
    if not tag_instance:
        tag_instance = Tag.get(Tag.tagname == in_tagname)
    recipetags = RecipeTags.select().where(RecipeTags.tagID == tag_instance.id).count()
    if recipetags == 0:
        tag_instance.delete_instance()


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
            taglist = sorted(t.tagname for t in thesetags)
        else:
            taglist = [{"name": t.tagname} for t in thesetags]
        # Todo: Get amount of recipies for earch tag
        thiscat = {
            "category": catname,
            "tags": taglist
        }
        data.append(thiscat)
    return data
