"""
Default configuration for recAPI backed.

Can be overwritten with default.py in instance folder.
"""

# Relative to application root
DATABASE = "data/database.yaml"
DATABASE_PATH = "data/database.sql"
IMAGE_PATH = "data/img"

# Relative to instance folder
TMP_DIR = "tmp"

ADMIN_PASSWORD = "password"

DEBUG = True
WSGI_HOST = "0.0.0.0"
WSGI_PORT = 9005

SECRET_KEY = "super secret key"
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "data/flask_session"
