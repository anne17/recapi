import os


class Config(object):
    """Paths and settings"""

    # Path to data base file
    DB_PATH = os.path.join(os.path.dirname(__file__), 'data/userdata.db')

    # Strings in data base:
    DB_MAIN = "users"
    DB_USERID = "id"
    DB_USER = "user"
    DB_PASSWORD = "password"
    DB_DISPLAYNAME = "display_name"
