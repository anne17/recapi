# recAPI

Flask REST-API for storing, editing and searching recipes.


## Prerequisites

* A Unix-like environment (e.g. Linux, OS X)
* [Python 3.6](http://python.org/) or newer
* mariaDB


## Installation

* Install the requirements, e.g. with virtualenv:

  ```
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

* Optional: create `config.py` inside the instance directory and adjust configuration.

## Running the backend

* Run in development mode (with `venv` activated):

  ```
  python run.py
  ```


# User CLI

Command line interface for administration of the user data base.

## Setup

Start serving the command-line API on a suitable port, e.g.:

```
  export FLASK_APP=recapi/user_cli.py FLASK_RUN_PORT=8083
```

## Command line options

Available commands:

* `flask add --user USER --display DISPLAY_NAME [--admin true|false]`: Creates a new user. Will prompt for password. Default value for admin is `false`

* `flask show --user USER`:  Displays user info.

* `flask showall`: Shows the entire user data base.

* `flask check --user USER`: Authenticates user `USER`. Will prompt for password.

* `flask deactivate --user USER`: Sets `USER`'s status to passive.

* `flask changepw --user USER`: Change password for `USER`.
