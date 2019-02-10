"""Abstract Meta class to be inherited from by all peewee models."""

import peewee as pw
# from flask import current_app

# from recapi.models.recipe import Recipe


class BaseModel(pw.Model):
    """Abstract base class for peewee models."""

    class Meta:
        """Meta information for model."""

        # db_path = current_app.config.get("DATABASE_PATH")
        db_path = "testdatabase.sql"
        database = pw.SqliteDatabase(db_path)


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


class DataBase():
    """Data base model for handling tables in peewee."""

    # db_path = current_app.config.get("DATABASE_PATH")
    db_path = "testdatabase.sql"

    def __init__(self):
        """Initialise SQL data base."""
        self.db = pw.SqliteDatabase(self.db_path)
        self.load_db()

    def load_db(self):
        """Load data base."""
        # current_app.logger.info("Resuming the data base")
        self.db.connect()
        self.db.create_tables([Recipe])

    def close_db(self):
        """Close connection to data base."""
        self.db.close()

    def remove_row(self, table, item_id):
        """Remove row with id from table."""
        row = table.get(table.id == item_id)
        row.delete_instance()

    def create_new_recipe(self, title, image="", source="", ingredients="", contents="", portions=0):
        """Test stuff."""
        recipe = Recipe(
            title=title,
            image=image,
            source=source,
            ingredients=ingredients,
            contents=contents,
            portions=portions
        )
        recipe.save()


if __name__ == '__main__':
    # For testing
    db = DataBase()
    db.create_new_recipe(
        title="New Recipe",
        source="mitt huvud",
        ingredients="blabla",
        portions=4
    )
    # remove_row(Recipe, 5)
