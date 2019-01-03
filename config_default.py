class Config:

    DATABASE = "data/database.yaml"
    DATABASE_PATH = "data/database.sql"

    # Path to media directory, relative to app.py
    MEDIA_DIR = "../static"

    DEBUG = True
    WSGI_HOST = "0.0.0.0"
    WSGI_PORT = 9005

    SECRET_KEY = "super secret key"
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "data/flask_session"
