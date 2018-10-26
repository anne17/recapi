import sys
import json
import click
from getpass import getpass
from flask import Flask

from db_communicate import UserDB

app = Flask(__name__)
UserDB = UserDB()


@app.cli.command()
def hello():
    """Greet the user."""
    click.echo('Hello!')


@app.cli.command()
def viewall():
    """View entire database."""
    pretty_response = json.dumps(UserDB, indent=2, sort_keys=True, ensure_ascii=False)
    click.echo(pretty_response)


@app.cli.command()
@click.option('--user', default="")
def viewuser(user):
    """Get the user's data set."""
    click.echo(UserDB.get(user))


@app.cli.command()
@click.option('--user', default="")
@click.option('--display', default="")
def adduser(user, display):
    """Adds a user to the data base."""
    pw = input_pw("Please select a password: ")
    try:
        UserDB.add_user(user, pw, display)
        click.echo("Successfully added user: %s" % user)
    except:
        click.echo("Unexpected error occurred! %s" % sys.exc_info()[0])


@app.cli.command()
@click.option('--user', default="")
def checkuser(user):
    """Check if password for user is correct."""
    pw = input_pw()
    try:
        if UserDB.check_user(user, pw):
            click.echo("Successfully authenticated user: %s" % user)
        else:
            click.echo("Invalid username or password!")
    except:
        click.echo("Unexpected error occurred! %s" % sys.exc_info()[0])


def input_pw(prompt="Password: "):
    """Prompt for password."""
    return getpass(prompt)
