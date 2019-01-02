import sys
import logging
import sqlite3

from flask import current_app

from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger('user_cli' + __name__)


class UserDB():
    """User data base model using sqlite."""

    def __init__(self, db_path=False):
        try:
            self.db_path = current_app.config.get("DATABASE_PATH")
        except RuntimeError:
            # When calling this from user_cli there is no app context.
            # Use db_path variable instead.
            self.db_path = db_path

        # Strings in data base:
        self.tablename = "users"
        self.db_userid = "id"
        self.db_user = "user"
        self.db_display = "display"
        self.db_password = "password"
        self.load_db()

    def __exit__(self):
        self.connection.commit()
        self.connection.close()

    def load_db(self):
        """Load sql data base."""
        log.info("Resuming the data base")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_table()

    def add_user(self, user, pw, displayname):
        """Add a new user to the data base."""
        if self.user_exists(user):
            log.error("User '%s' already exists!", user)
            raise Exception(f"User '{user}' already exists!")
        try:
            sql = (
                f"INSERT INTO {self.tablename} "
                f"({self.db_user}, {self.db_display}, {self.db_password}) "
                f"values (?, ?, ?)"
            )
            self.cursor.execute(sql, (
                user,
                displayname,
                generate_password_hash(pw)
            ))
            self.connection.commit()
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            raise Exception(f"Could not save changes to database! {e}")

    def update_pw(self, user, pw):
        """Change a user's password."""
        if not self.user_exists(user):
            raise Exception(f"User '{user}' does not exist!")
        try:
            sql = (
                f"UPDATE {self.tablename} "
                f"SET {self.db_password} = ? WHERE {self.db_user} = ?"
            )
            self.cursor.execute(sql, (generate_password_hash(pw), user))
            self.connection.commit()
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            raise Exception(f"Could not save changes to database! {e}")

    def get(self, user):
        sql = f"SELECT * FROM {self.tablename} WHERE {self.db_user}=?"
        self.cursor.execute(sql, (user,))
        u = self.cursor.fetchone()
        if not u:
            log.error(f"Error: unknown user: {user}")
            return False
        else:
            return u

    def getall(self):
        sql = (f"SELECT {self.db_userid}, {self.db_user}, {self.db_display} "
               f"FROM {self.tablename}")
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def check_user(self, user, pw):
        """Check if user's password is correct."""
        sql = (
            f"SELECT {self.db_password} "
            f"FROM {self.tablename} "
            f"WHERE {self.db_user}=?"
        )
        self.cursor.execute(sql, (user,))
        stored_pw = self.cursor.fetchone()[0]
        return check_password_hash(stored_pw, pw)

    def delete_user(self, user):
        """Remove user from data base."""
        sql = f"DELETE FROM {self.tablename} WHERE {self.db_user}=?"
        try:
            self.cursor.execute(sql, (user,))
            assert (self.cursor.rowcount == 1)
            self.connection.commit()
        except Exception as e:
            log.error("Could not delete user! %s", e)
            raise Exception(f"Could not delete user! {e}")

    def user_exists(self, user):
        """Check if user exists in data base."""
        sql = f"SELECT {self.db_user} FROM {self.tablename}"
        self.cursor.execute(sql)
        users = [u[0] for u in self.cursor.fetchall()]
        if user in users:
            return True
        return False

    def create_table(self):
        """Create the user data table if it does not exist."""
        sql = (
            f"CREATE TABLE IF NOT EXISTS {self.tablename} "
            f"({self.db_userid} INTEGER PRIMARY KEY AUTOINCREMENT, "
            f"{self.db_user}, "
            f"{self.db_display}, "
            f"{self.db_password})")
        self.cursor.execute(sql)

    def get_by_id(self, uid):
        """Get user by ID."""
        sql = f"SELECT * FROM {self.tablename} WHERE {self.db_userid}=?"
        self.cursor.execute(sql, (int(uid),))
        return self.cursor.fetchone()
