
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import login_manager


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        # a property that is True if the user has valid credentials or False otherwise.
        return True

    def is_active(self):
        # a property that is True if the user's account is active or False otherwise.
        return True

    def is_anonymous(self):
        # a property that is False for regular users, and True for a special, anonymous user.
        return True

    def get_id(self):
        # a method that returns a unique identifier for the user as a string (unicode, if using Python 2).
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
