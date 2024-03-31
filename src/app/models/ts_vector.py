"""
This module contains the TSVector class which is a subclass of TypeDecorator.
"""

from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator

class TSVector(TypeDecorator):
    """
    Represents a PostgreSQL tsvector column type.

    This class is a custom SQLAlchemy type decorator
    that maps the tsvector column type in PostgreSQL
    to a Python class. It allows seamless integration
    of tsvector columns in SQLAlchemy models.

    Usage:
    ------
    Define a column in your SQLAlchemy model with the `TSVector` type decorator:

    class MyModel(Base):
        __tablename__ = 'my_table'
        id = Column(Integer, primary_key=True)
        tsvector_column = Column(TSVector)

    Note:
    -----
    The `TSVector` type decorator requires the `psycopg2` package to be installed.

    """

    impl = TSVECTOR
