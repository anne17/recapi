# User CLI

Command line interface for administration of the user data base.

## Setup

* Setup python 3 virtual environment:

```
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
```

* Create data directory
* Run command-line API (virtualenv must be activated):

```
    export FLASK_APP=cmd_api.py FLASK_RUN_PORT=8083
```

## Admin API specifications

From the command-line

#### adduser

    flask adduser --user USER --display DISPLAY_NAME

Creates an user with username `USER`, and display name `DISPLAY_NAME`.
Will prompt for password.

#### viewuser

    flask viewuser --user USER

Displays user ID, username, displayname in stdout.

#### viewall

    flask viewall

Shows entire user database.

#### checkuser

    flask checkuser --user USER

Authenticates user `USER`. Will prompt for password.

#### deleteuser

    flask deleteuser --user USER

Deletes user from data base.
