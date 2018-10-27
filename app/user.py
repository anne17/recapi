
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

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
        assert (len(userdata) == 4)
        self.is_authenticated = self.authenticate(self.userdata[3])
        self.userid = self.userdata[0]
        self.displayname = self.userdata[2]

    def authenticate(self, user_password):
        """Set is_authenticated to True if the user has valid credentials (False otherwise)."""
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
        return str(self.userid)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
