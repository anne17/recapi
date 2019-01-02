from werkzeug.security import check_password_hash

from recipe.db_communicate import UserDB


class User():
    def __init__(self, username):
        """User model"""
        self.username = username

        # Retrieve user information from data base.
        userdb = UserDB()
        userdata = userdb.get(self.username)
        if userdata:
            self.user_password = userdata[3]
            self.displayname = userdata[2]
        else:
            self.user_password = False
            self.displayname = ""

    def is_authenticated(self, password):
        """Return True if the user has valid credentials (False otherwise)."""
        if not self.user_password:
            return False
        return check_password_hash(self.user_password, password)
