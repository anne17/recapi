import sqlite3

from app import Config


class RecipeTable():
    """User data base model using sqlite."""

    def __init__(self):
        self.db_path = Config.get("DB", "db_path")
        self.tablename = Config.get("DB", "recipe_table")
        self.id = Config.get("DB", "recipe_id")
        self.name = Config.get("DB", "recipe_name")
        self.content = Config.get("DB", "recipe_content")
        self.ingredients = Config.get("DB", "recipe_ingredients")
        self.created_by = Config.get("DB", "recipe_created")

        self.tags_tablename = Config.get("DB", "tags_table")
        self.tag_id = Config.get("DB", "tag_id")
        self.tag_name = Config.get("DB", "tag_name")

        self.load_db()

    def __exit__(self):
        self.connection.commit()
        self.connection.close()

    def load_db(self):
        """Load sql data base."""
        # log.info("Resuming the data base")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_table()

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
            sql = ("INSERT INTO %s values (?, ?, ?, ?, ?)" % self.tablename)
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

    def create_table(self):
        """Create the user data table if it does not exist."""
        sql = "CREATE TABLE IF NOT EXISTS %s (%s, %s, %s, %s, %s)" % (
              self.tablename,
              self.name,
              self.content,
              self.ingredients,
              self.created_by
        )
        self.cursor.execute(sql)
