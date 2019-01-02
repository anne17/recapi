import sqlite3

from flask import current_app


class RecipeTable():
    """User data base model using sqlite."""

    def __init__(self):
        # recipe_tag_id = tag_id
        #
        # tag_meta_table = recipe_tags
        # tag_meta_id = rowid
        # tag_meta_recipe_id = recipe_id
        # tag_meta_tag_id = tag_id
        self.db_path = current_app.config.get("DATABASE_PATH")
        self.tablename = "recipies"
        self.id = "id"
        self.name = "recipe"
        self.content = "content"
        self.ingredients = "ingredients"
        self.image = "image"
        self.created_by = "created_by"

        self.tags_tablename = "tags"
        self.tag_id = "tag_id"
        self.tag_name = "tag_name"

        self.load_db()

    def __exit__(self):
        self.connection.commit()
        self.connection.close()

    def load_db(self):
        """Load sql data base."""
        # log.info("Resuming the data base")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def add_recipe(self, data):
        """Add a new recipe to the data base."""
        tags = data.get("tags")
        for tag in tags:
            pass
            # add row in tag meta table
        # if self.user_exists(user):
        #     log.error("User '%s' already exists!" % user)
        #     raise Exception("User '%s' already exists!" % user)
        try:
            sql = (f"INSERT INTO {self.tablename} values (?, ?, ?, ?, ?)")
            self.cursor.execute(sql, (
                data.get("name"),
                data.get("content"),
                data.get("ingredients"),
                data.get("user"),
            ))
            self.connection.commit()
        except Exception as e:
            # log.error("Could not save changes to database! %s", e)
            raise Exception("Could not save changes to database! %s" % e)

    def create_tables(self):
        """Create the user data table if it does not exist."""
        sql = (
            f"CREATE TABLE IF NOT EXISTS {self.tablename} ("
            f"{self.id} INTEGER PRIMARY KEY AUTOINCREMENT, "
            f"{self.name}, "
            f"{self.image}, "
            f"{self.content}, "
            f"{self.ingredients}, "
            f"{self.created_by}, "
            f"{self.tags}) "
            f"FOREIGN KEY({self.created_by}) REFERENCES users(id) "  # Todo: Don't hard-code this!
            # f"FOREIGN KEY({self.tags}) REFERENCES tags(id)"
        )
        self.cursor.execute(sql)
