"""
Default configuration for recAPI backed.

Can be overwritten with config.py in instance folder.
"""

import datetime

# Paths relative to the instance folder
TMP_DIR = "tmp"
IMAGE_PATH = "img"
THUMBNAIL_PATH = "thumb"
MEDIUM_IMAGE_PATH = "img_medium"

ADMIN_PASSWORD = "password"

DEBUG = True
WSGI_HOST = "0.0.0.0"
WSGI_PORT = 9005

SECRET_KEY = "super secret key"
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "instance/flask_session"
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=90)

# SQL database info
DB_NAME = "recipe"
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = "127.0.0.1"
DB_PORT = 3306

# List of randomizer tags (for /random route)
RANDOM_TAGS = ["lunch/middag"]

# Email config
EMAIL_FROM = ""
EMAIL_TO = []        # Adresses for all admin users
EMAIL_TO_ADMIN = []  # Adresses for admin mails such as error reports
