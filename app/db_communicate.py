import os
import sys
import logging
import configparser
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger('user_cli' + __name__)


# Read config
if os.path.exists(os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'config.cfg')) is False:
    configfile = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'config.default.cfg')
else:
    configfile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.cfg')

Config = configparser.ConfigParser()
Config.read(configfile)


class UserDB():
    """User data base model using sqlite."""

    def __init__(self):
        self.db_path = Config.get("USER_DB", "db_path")
        self.tablename = Config.get("USER_DB", "db_users_table")
        self.db_userid = Config.get("USER_DB", "db_userid")
        self.db_user = Config.get("USER_DB", "db_user")
        self.db_display = Config.get("USER_DB", "db_display")
        self.db_password = Config.get("USER_DB", "db_password")
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
            sql = ("INSERT INTO %s values (?, ?, ?, ?)" % self.tablename)
            self.cursor.execute(sql, (
                          self.gen_id(),
                          user,
                          displayname,
                          generate_password_hash(pw)
                      ))
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
        sql = "CREATE TABLE IF NOT EXISTS %s (%s, %s, %s, %s)" % (
                self.tablename,
                self.db_userid,
                self.db_user,
                self.db_display,
                self.db_password
                )
        self.cursor.execute(sql)

    def gen_id(self):
        """Generate unique ID for new user."""
        sql = "SELECT %s FROM %s" % (self.db_userid, self.tablename)
        self.cursor.execute(sql)
        uids = [uid[0] for uid in self.cursor.fetchall()]
        uids.append(0)  # fallback
        ID_count = max(uids) + 1
        return ID_count
