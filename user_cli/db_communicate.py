import os
import sys
import logging
import json
import configparser
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger('user_cli' + __name__)


# Read config
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.cfg')) is False:
    configfile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.default.cfg')
else:
    configfile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.cfg')

Config = configparser.ConfigParser()
Config.read(configfile)


class UserDB():
    def __init__(self):
        self.db_path = Config.get("USER_CLI", "db_path")
        self.tablename = Config.get("USER_CLI", "db_users_table")
        self.db_userid = Config.get("USER_CLI", "db_userid")
        self.db_user = Config.get("USER_CLI", "db_user")
        self.db_display = Config.get("USER_CLI", "db_display")
        self.db_password = Config.get("USER_CLI", "db_password")

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.load_db()

        # TODO disconnect, save

    def load_db(self):
        """Read all the json data in Config.db_path and save it as a dictionary."""
        log.info("Resuming the data base")
        # Create table if it does not exist
        self.create_table()

    def add_user(self, user, pw, displayname):
        """Add a new user to the data base."""
        if self.user_exists(user):
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
        # TODO: get data for one user
        return "Not implemented yet"
        # if not UserDB.get(user):
        #     click.echo("Error: unknown user: %s" % user)
        # else:
        #     pretty_response = json.dumps(UserDB[user], indent=2, sort_keys=True, ensure_ascii=False)
        #     click.echo(pretty_response)

    def user_exists(self, user):
        # TODO
        return False

    def create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS %s (%s, %s, %s, %s)" % (
                self.tablename,
                self.db_userid,
                self.db_user,
                self.db_display,
                self.db_password
                )
        self.cursor.execute(sql)

    def gen_id(self):
        # TODO
        sql = "SELECT %s from %s" % (self.db_userid, self.tablename)
        self.cursor.execute(sql)
        print(self.cursor.fetchall())
        return 1
        # ids = [0]
        # for userdata in db.values():
        #     ids.append(userdata.get(Config.get("USER_CLI", "db_userid"), 0))
        # ID_count = max(ids)
        # ID_count += 1
        # return ID_count

    def check_user(self, user, pw, db):
        """Check if user's password is correct."""
        return check_password_hash(db.get(user)[Config.get("USER_CLI", "db_password")], pw)
