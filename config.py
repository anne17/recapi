"""
Default configuration for recAPI backed.

Can be overwritten with config.py in instance folder.
"""

# Paths relative to the instance folder
TMP_DIR = "tmp"
IMAGE_PATH = "img"

ADMIN_PASSWORD = "password"

DEBUG = True
WSGI_HOST = "0.0.0.0"
WSGI_PORT = 9005

SECRET_KEY = "super secret key"
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "instance/flask_session"

# SQL database info
DB_NAME = "recipe"
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = "127.0.0.1"
DB_PORT = 3306
