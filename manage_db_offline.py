"""Offline management of database."""

import os

import peewee as pw
import playhouse.migrate

from recapi.models import usermodel
from recapi.models import DATABASE
import config
# Overwrite with instance config
if os.path.exists(os.path.join("instance", "config.py")):
    import instance.config as config


def init_db():
    """Initialise database."""
    DATABASE.init(
        config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT)
    config.SQLDB = DATABASE


def update_db():
    """Do some updates."""
    migrator = playhouse.migrate.MySQLMigrator(config.SQLDB)

    # Check documentation for more info:
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations

    # Some examples for altering data
    playhouse.migrate.migrate(
        # Add column with or without foreign key
        # migrator.add_column("recipe", "changed_by_id", pw.ForeignKeyField(usermodel.User, null=True, field=usermodel.User.id)),
        # migrator.add_column("recipe", "changed", pw.DateTimeField(null=True))

        # Drop column
        # migrator.drop_column('recipe', 'changed_by'),
    )


if __name__ == '__main__':
    init_db()
    update_db()
