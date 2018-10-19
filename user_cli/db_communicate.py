import os
import sys
import logging
import json
import configparser

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


def load_db():
    """Read all the json data in Config.db_path and save it as a dictionary."""
    log.info("Resuming the data base")
    if os.path.isfile(Config.get("USER_CLI", "db_path")):
        with open(Config.get("USER_CLI", "db_path"), "r") as f:
            userDB = json.load(f)
    else:
        userDB = {}
    return userDB


def add_user(user, pw, displayname, db):
    """Add a new user to the data base."""
    if not db.get(user):
        db[user] = {}
        db[user][Config.get("USER_CLI", "db_password")] = generate_password_hash(pw)
        db[user][Config.get("USER_CLI", "db_display")] = displayname
        db[user][Config.get("USER_CLI", "db_userid")] = gen_id(db)

        try:
            save_userdb(db)
        except Exception as e:
            log.error("Could not save changes to database! %s", e)
            raise Exception("Could not save changes to database! %s" % e)

    else:
        raise Exception("User '%s' already exists!" % user)


def save_userdb(userdb):
    """Save data base to file."""
    with open(Config.get("USER_CLI", "db_path"), "w") as f:
        json.dump(userdb, f)


def gen_id(db):
    ids = [0]
    for userdata in db.values():
        ids.append(userdata.get(Config.get("USER_CLI", "db_userid"), 0))
    ID_count = max(ids)
    ID_count += 1
    return ID_count


def check_user(user, pw, db):
    """Check if user's password is correct."""
    return check_password_hash(db.get(user)[Config.get("USER_CLI", "db_password")], pw)
