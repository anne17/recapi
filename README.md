# recAPI

Flask REST-API for storing, editing and searching recipes.


## Prerequisites

* A Unix-like environment (e.g. Linux, OS X)
* [Python 3.6](http://python.org/) or newer
* pipenv


## Installation

* Install the requirements with pipenv:

    ```
    pipenv install
    ```
* Copy file `config_default.py` to `config.py` and adjust configuration.

## Running the backend

* Run in development mode:

    ```
    pipenv run python run.py
    ```


# User CLI

Command line interface for administration of the user data base.

## Setup

Start serving the command-line API on a suitable port, e.g.:

```
    export FLASK_APP=recapi/user_cli.py FLASK_RUN_PORT=8083
```

## Command line options

Prefix every command with `pipenv run flask`.

Available commands:

* `add --user USER --display DISPLAY_NAME --admin true|false`: Creates a new user. Will prompt for password.

* `show --user USER`:  Displays user ID, username, displayname in stdout.

* `showall`: Shows the entire user data base.

* `check --user USER`: Authenticates user `USER`. Will prompt for password.

* `deactivate --user USER`: Sets `USER`'s status to passive.

* `changepw --user USER`: Change password for `USER`.
