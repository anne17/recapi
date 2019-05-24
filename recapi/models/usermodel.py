"""Collection of different models to communicate with the data base."""

import peewee as pw
from playhouse.shortcuts import model_to_dict
from werkzeug.security import check_password_hash, generate_password_hash

from recapi.models import BaseModel


class User(BaseModel):
    """User table (peewee model)."""

    displayname = pw.CharField()
    username = pw.CharField(unique=True, max_length="20")
    password = pw.CharField()
    admin = pw.BooleanField(default=False)
    active = pw.BooleanField()

    def is_authenticated(self, check_password):
        """Return True if the user has valid credentials (False otherwise)."""
        if not self.password:
            return False
        return check_password_hash(self.password, check_password)


def add_user(username, password, displayname, admin=False):
    """Add new user to db."""
    try:
        user = User(
            username=username,
            password=generate_password_hash(password),
            displayname=displayname,
            admin=admin,
            active=True
        )
        user.save()
    except pw.IntegrityError:
        raise Exception("Username already exists!")


def show_user(in_username):
    """Show information for one user."""
    user = User.get(User.username == in_username)
    userdict = model_to_dict(user)
    userdict.pop("password")
    return userdict


def show_all_users():
    """Return a summary of all users in the database."""
    users = User.select()
    data = {}
    for user in users:
        userdict = model_to_dict(user)
        userdict.pop("password")
        data[user.username] = userdict
    return data


def get_user(in_username):
    """Retrieve a user's data by username."""
    return User.get(User.username == in_username)


def check_user(in_username, in_password):
    """Check if password for user is correct."""
    user = User.get(User.username == in_username)
    return check_password_hash(user.password, in_password)


def update_password(in_username, in_password):
    """Update a user's password."""
    user = User.get(User.username == in_username)
    user.password = generate_password_hash(in_password)
    user.save()


def deactivate_user(in_username):
    """Change a user's status to passive."""
    user = User.get(User.username == in_username)
    user.active = False
    user.save()
