# recAPI

Flask REST-API for storing, editing and searching recipes.

## Prerequisites

* A Unix-like environment (e.g. Linux, OS X)
* [Python 3.10](http://python.org/) or newer
* mariaDB

## Installation

* Install the requirements with uv:

  ```bash
  uv sync
  ```

* Optional: create `config.py` inside the instance directory and adjust configuration.

### MariaDB setup

* Create a database and a user with access to it. For example:

  ```sql
  CREATE DATABASE recipe;
  CREATE USER 'recapi'@'localhost' IDENTIFIED BY 'password';
  GRANT ALL PRIVILEGES ON recipe.* TO 'recapi'@'localhost';
  ```

## Running the app in development mode

  ```bash
  uv run recapi
  ```

Now the app is running at <http://localhost:9005/>.

## Production deployment

On the server, install the locked production dependencies before restarting the application:

```bash
uv sync --locked --no-dev
```

Use Supervisor to run Gunicorn from uv's managed virtual environment. This starts Gunicorn directly and avoids resolving
dependencies when the service starts:

```ini
[program:recapi]
command=[PATH_TOA_APP]/.venv/bin/gunicorn -t 200 --chdir [PATH_TOA_APP]/recapi --log-file [PATH_TOA_APP]/instance/logs/
gunicorn.log -b localhost:8081 recapi:create_app()
directory=[PATH_TOA_APP]
stdout_logfile=[PATH_TOA_APP]/instance/logs/supervisord.log
redirect_stderr=true
user=anne
environment=HOME="/home/anne"
```

## User CLI

The built-in command line interface can be used for administration of the user data base (i.e. adding users, changing
passwords, etc.). The commands are:

`uv run recapi-user-cli --help` # Displays help for the user CLI.
`uv run recapi-user-cli add --user USER --display "DISPLAY NAME" [--admin true|false]` # Creates a new user. Will prompt
for password. Default value for admin is `false`
`uv run recapi-user-cli show --user USER` # Displays user info.
`uv run recapi-user-cli showall` # Shows the entire user data base.
`uv run recapi-user-cli check --user USER` # Authenticates user `USER`. Will prompt for password.
`uv run recapi-user-cli deactivate --user USER` # Sets `USER`'s status to passive.
`uv run recapi-user-cli changepw --user USER` # Change password for `USER`.
