"""Command line interface for administering the user data base."""

import os

import click
from flask import Flask
from getpass import getpass

from recapi.models import DATABASE, usermodel

app = Flask(__name__)

# Set default config
app.config.from_object("config")

# Overwrite with instance config
if os.path.exists(os.path.join(app.instance_path, "config.py")):
    app.config.from_pyfile(os.path.join(app.instance_path, "config.py"))

DATABASE.init(
    app.config.get("DB_NAME"),
    user=app.config.get("DB_USER"),
    password=app.config.get("DB_PASSWORD"),
    host=app.config.get("DB_HOST"),
    port=app.config.get("DB_PORT"))
usermodel.User.create_table()
app.config["SQLDB"] = DATABASE


@app.cli.command()
def showall():
    """View entire database."""
    users = usermodel.show_all_users()
    if not users:
        click.echo("Data base is empty!")
    else:
        for username, values in users.items():
            click.echo(stringify_user_info(values))


@app.cli.command()
@click.option("--user", default="")
def show(user):
    """Get the user's data set."""
    userinfo = usermodel.show_user(user)
    click.echo(stringify_user_info(userinfo))


@app.cli.command()
@click.option("--user", default="")
@click.option("--display", default="")
@click.option("--admin", default="true")
def add(user, display, admin):
    """Add a user to the data base."""
    if admin.lower() not in ["true", "false"]:
        click.echo("'admin' must be 'true' or 'false'")
        return
    pw = input_pw("Please select a password: ")
    pw2 = input_pw("Please confirm password: ")
    if pw != pw2:
        click.echo("Password not confirmed. Aborting.")
        exit()
    try:
        usermodel.add_user(user, pw, display, admin)
        click.echo("Successfully added user: %s" % user)
    except Exception as e:
        click.echo("Error: %s" % e)


@app.cli.command()
@click.option("--user", default="")
def check(user):
    """Check if password for user is correct."""
    pw = input_pw()
    try:
        if usermodel.show_user(user, pw):
            click.echo("Successfully authenticated user: %s" % user)
        else:
            click.echo("Invalid username or password!")
    except Exception as e:
        click.echo("Unexpected error occurred! %s" % e)


@app.cli.command()
@click.option("--user", default="")
def changepw(user):
    """Change password for user."""
    pw = input_pw("Please enter new password: ")
    pw2 = input_pw("Please confirm password: ")
    if pw != pw2:
        click.echo("Password not confirmed. Aborting.")
        exit()
    try:
        usermodel.update_password(user, pw)
        click.echo("Successfully changed password for user: %s" % user)
    except Exception as e:
        click.echo("Unexpected error occurred! %s" % e)


@app.cli.command()
@click.option("--user", default="")
def deactivate(user):
    """Set status passive on user."""
    try:
        usermodel.deactivate_user(user)
        click.echo("Deactivated user: %s" % user)
    except Exception as e:
        click.echo("Unexpected error occurred! %s" % e)


def input_pw(prompt="Password: "):
    """Prompt for password."""
    return getpass(prompt)


def stringify_user_info(userdict):
    """Turn user info into string."""
    user_status = "active" if userdict.get("active") is True else "passive"
    return 'username: "%s" displayname: id: "%s" "%s" status: "%s" admin: %s' % (
        userdict.get("username"),
        userdict.get("displayname"),
        userdict.get("id"),
        user_status,
        userdict.get("admin")
    )
