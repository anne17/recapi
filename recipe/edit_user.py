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
            log.error("User '%s' already exists!" % user)
            raise Exception("User '%s' already exists!" % user)
        try:
            sql = ("INSERT INTO %s (%s, %s, %s) values (?, ?, ?)" % (
                   self.tablename,
                   self.db_user,
                   self.db_display,
                   self.db_password))
            self.cursor.execute(sql, (
                user,
                displayname,
                generate_password_hash(pw)
            ))
            self.connection.commit()
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            raise Exception("Could not save changes to database! %s" % e)

    def update_pw(self, user, pw):
        """Change a user's password."""
        if not self.user_exists(user):
            raise Exception("User '%s' does not exist!" % user)
        try:
            sql = ("UPDATE %s SET %s = ? WHERE %s= ?" % (
                   self.tablename,
                   self.db_password,
                   self.db_user))
            print(sql)
            self.cursor.execute(sql, (generate_password_hash(pw), user))
            self.connection.commit()
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            raise Exception("Could not save changes to database! %s" % e)

    def get(self, user):
        sql = "SELECT * FROM %s WHERE %s=?" % (
            self.tablename,
            self.db_user
        )
        self.cursor.execute(sql, (user,))
        u = self.cursor.fetchone()
        if not u:
            log.error("Error: unknown user: %s" % user)
            return False
        else:
            return u

    def getall(self):
        sql = "SELECT %s, %s, %s FROM %s" % (
            self.db_userid,
            self.db_user,
            self.db_display,
            self.tablename
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def check_user(self, user, pw):
        """Check if user's password is correct."""
        sql = "SELECT %s FROM %s WHERE %s=?" % (
            self.db_password,
            self.tablename,
            self.db_user
        )
        self.cursor.execute(sql, (user,))
        stored_pw = self.cursor.fetchone()[0]
        return check_password_hash(stored_pw, pw)

    def delete_user(self, user):
        """Remove user from data base."""
        sql = "DELETE FROM %s WHERE %s=?" % (
            self.tablename,
            self.db_user
        )
        try:
            self.cursor.execute(sql, (user,))
            assert (self.cursor.rowcount == 1)
            self.connection.commit()
        except Exception as e:
            log.error("Could not delete user! %s", e)
            raise Exception("Could not delete user! %s" % e)

    def user_exists(self, user):
        """Check if user exists in data base."""
        sql = "SELECT %s FROM %s" % (
            self.db_user,
            self.tablename
        )
        self.cursor.execute(sql,)
        users = [u[0] for u in self.cursor.fetchall()]
        if user in users:
            return True
        return False

    def create_table(self):
        """Create the user data table if it does not exist."""
        sql = "CREATE TABLE IF NOT EXISTS %s (%s INTEGER PRIMARY KEY AUTOINCREMENT, %s, %s, %s)" % (
              self.tablename,
              self.db_userid,
              self.db_user,
              self.db_display,
              self.db_password
        )
        self.cursor.execute(sql)

    def get_by_id(self, uid):
        """Get user by ID."""
        sql = "SELECT * FROM %s WHERE %s=?" % (
            self.tablename,
            self.db_userid
        )
        self.cursor.execute(sql, (int(uid),))
        return self.cursor.fetchone()
