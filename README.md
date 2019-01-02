# receptsida-backend


## Prerequisites

* A Unix-like environment (e.g. Linux, OS X)
* [Python 3.4](http://python.org/) or newer
* pipenv


## Installation

* Install the requirements with pipenv:

    ```
    pipenv install
    ```

## Running the backend

* Run in development mode:

    ```
    pipenv run python run.py
    ```


# User CLI

Command line interface for administration of the user data base.

## Setup

Start serving the command-line API:

```
    export FLASK_APP=recipe/user_cli.py FLASK_RUN_PORT=8083
```

## Command line options

    pipenv run flask adduser --user USER --display DISPLAY_NAME

Creates an user with username `USER`, and display name `DISPLAY_NAME`.
Will prompt for password.


    pipenv run flask viewuser --user USER

Displays user ID, username, displayname in stdout.


    pipenv run flask viewall

Shows the entire user data base.


    pipenv run flask checkuser --user USER

Authenticates user `USER`. Will prompt for password.


    pipenv run flask deleteuser --user USER

Deletes user from data base.
