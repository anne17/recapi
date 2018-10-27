# receptsida-backend


## Prerequisites

* A Unix-like environment (e.g. Linux, OS X)
* [Python 3.4](http://python.org/) or newer


## Installation

* Create a Python 3 virtual environment and install the requirements:

    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Running the backend

* For development mode run (while venv is active):

    ```
    python app.py
    ```


# User CLI

Command line interface for administration of the user data base.

## Setup

Start venv and run command-line API:

```
    source venv/bin/activate
    export FLASK_APP=app/cmd_api.py FLASK_RUN_PORT=8083
```

## Command line options

    flask adduser --user USER --display DISPLAY_NAME

Creates an user with username `USER`, and display name `DISPLAY_NAME`.
Will prompt for password.


    flask viewuser --user USER

Displays user ID, username, displayname in stdout.


    flask viewall

Shows the entire user data base.


    flask checkuser --user USER

Authenticates user `USER`. Will prompt for password.


    flask deleteuser --user USER

Deletes user from data base.
