
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import utils
from app import Config, login_manager


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.db_pw_attr = Config.get("USER_DB", "db_password")
        self.db_id_attr = Config.get("USER_DB", "db_userid")

        self.load_db()
        self.userdata = self.db.get(self.username, "")

        self.is_authenticated = self.authenticate()

    def load_db(self):
        self.db = utils.load_data(Config.get("USER_DB", "db_path"))

    def authenticate(self):
        """Set is_authenticated to True if the user has valid credentials (False otherwise)."""
        user_password = self.userdata.get(self.db_pw_attr)
        authenticated = check_password_hash(user_password, generate_password_hash(self.password))
        return authenticated

    def is_active(self):
        # a property that is True if the user's account is active or False otherwise.
        return True

    def is_anonymous(self):
        # a property that is False for regular users, and True for a special, anonymous user.
        return True

    def get_id(self):
        """Return a unique identifier for the user as a string."""
        return str(self.userdata.get(self.db_id_attr))


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
