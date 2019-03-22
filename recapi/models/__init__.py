"""Abstract Meta class to be inherited from by all peewee models."""

import peewee as pw

DATABASE = pw.MySQLDatabase(None)


class BaseModel(pw.Model):
    """Abstract base class for peewee models."""

    class Meta:
        """Meta information for model."""

        database = DATABASE
