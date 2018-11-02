from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app import login_manager
from db_communicate import UserDB


class User(UserMixin):
    def __init__(self):
        self.username = ""
        self.id = self.username
        self.user_password = ""
        self.displayname = ""

    def init_user(self):
        """Retrieve user information from data base."""
        userdb = UserDB()
        userdata = userdb.get(self.username)
        if userdata:
            self.user_password = userdata[3]
            self.displayname = userdata[2]

    def is_authenticated(self, password):
        """Return True if the user has valid credentials (False otherwise)."""
        self.init_user()
        return check_password_hash(self.user_password, password)

    def is_active(self):
        """Return True if the user's account is active or False otherwise."""
        return True

    def is_anonymous(self):
        """Return False for regular users, and True for a special, anonymous user."""
        return False

    def get_id(self):
        """Return a unique identifier for the user as a string."""
        return str(self.username)


@login_manager.user_loader
def load_user(username):
    user = User()
    user.username = username
    return user
