
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app import login_manager
from db_communicate import UserDB


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.init_user()

    def init_user(self):
        userdb = UserDB()
        userdata = userdb.get(self.username)
        if not userdata:
            userdata = (0, "", "", "")
        self.user_password = userdata[3]
        self.displayname = userdata[2]
        self.userid = userdata[0]

    def is_authenticated(self):
        """Return True if the user has valid credentials (False otherwise)."""
        return check_password_hash(self.user_password, self.password)

    def is_active(self):
        # a property that is True if the user's account is active or False otherwise.
        return True

    def is_anonymous(self):
        # a property that is False for regular users, and True for a special, anonymous user.
        return True

    def get_id(self):
        """Return a unique identifier for the user as a string."""
        return str(self.userid)

    def get(uid):
        """Get user by ID."""
        userdb = UserDB()
        user = userdb.get_by_id(uid)
        print("user:", user)
        # needs to return User object??
        return user


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
