import os
import sys
import logging
import json
from config import Config

from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger('user_cli' + __name__)


def load_db():
    """Read all the json data in Config.DB_PATH and save it as a dictionary."""
    log.info("Resuming the data base")
    if os.path.isfile(Config.DB_PATH):
        with open(Config.DB_PATH, "r") as f:
            userDB = json.load(f)
    else:
        userDB = {}
    # TODO: Collect IDs!
    return userDB


def add_user(user, pw, db):
    """Add a new user to the data base."""
    if not db.get(user):
        db[user] = {}
        db[user][Config.DB_USER] = user
        db[user][Config.DB_PASSWORD] = generate_password_hash(pw)
        # db[user][Config.DB_DISPLAYNAME] =
        # db[user][Config.DB_USERID] = gen_id()

        try:
            save_userdb(db)
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            print("Could not save changes to database! %s" % e)

    else:
        raise Exception("User '%s' already exists!" % user)


def save_userdb(userdb):
    """Save data base to file."""
    with open(Config.DB_PATH, "w") as f:
        json.dump(userdb, f)


def gen_id():
    # TODO
    return 1


def check_user(user, pw, db):
    return check_password_hash(db.get(user)[Config.DB_PASSWORD], pw)
