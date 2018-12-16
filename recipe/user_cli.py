import sys
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
    users = UserDB.getall()
    if not users:
        click.echo("Data base is empty!")
    else:
        for u in users:
            click.echo(u)


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
    pw2 = input_pw("Please confirm password: ")
    if pw != pw2:
        click.echo("Password not confirmed. Aborting.")
        exit()
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


@app.cli.command()
@click.option('--user', default="")
def deleteuser(user):
    """Deletes a user from the data base."""
    try:
        UserDB.delete_user(user)
        click.echo("Deleted user: %s" % user)
    except:
        click.echo("Unexpected error occurred! %s" % sys.exc_info()[0])


def input_pw(prompt="Password: "):
    """Prompt for password."""
    return getpass(prompt)
