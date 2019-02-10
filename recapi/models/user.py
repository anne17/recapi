"""Collection of different models to communicate with the data base."""

from werkzeug.security import check_password_hash
# import peewee as pw

from recapi.edit_user import UserDB
# from recapi.models import BaseModel


class User():
    """User model."""

    def __init__(self, username):
        """Retrieve the user's data from the data base."""
        self.username = username

        userdb = UserDB()
        userdata = userdb.get(self.username)
        if userdata:
            self.user_password = userdata[3]
            self.displayname = userdata[2]
            self.uid = userdata[0]
        else:
            self.user_password = False
            self.displayname = ""
            self.uid = 0

    def is_authenticated(self, password):
        """Return True if the user has valid credentials (False otherwise)."""
        if not self.user_password:
            return False
        return check_password_hash(self.user_password, password)


# class User2(BaseModel):
#     """User model (peewee)."""
#
#     user = pw.TextField()
#     display = pw.TextField()
#     password = pw.TextField()
