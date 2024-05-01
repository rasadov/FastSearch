"""
This module contains utility functions for database control.

Main purpose of this file is to perform some of operations on local machine, not on the web server.
In case if web server is not powerful enough to handle the operations,
we can perform the operations on local machine.

The functions in this module are used to perform various operations on the database,
such as creating tables, executing SQL statements, and granting privileges.

Functions:
----------
- clear: Clear the console screen.
- execute_sql_statement(query: str): Execute the specified SQL statement in the database.
- create_tables(): Create the tables in the database.
- create_owner_account(
    owner_email: str = OWNER_EMAIL,
    confirmation_date: datetime = SERVER_STARTED_ON):
    Create an owner account with the specified email address and confirmation date.
- grant_privileges(db_name: str, db_user: str): 
    Grant all privileges on the specified database to the specified user.
- create_extension(extension_name: str = "pg_trgm"):
Create the specified extension in the database.
"""

import os
import sys
import time

from sqlalchemy import text

from spiders.myproject.myproject.spiders import MySpider
from src.app.__init__ import app, db, OWNER_EMAIL, SERVER_STARTED_ON
from src.app.models import User, Product, PriceHistory, Cart, Message

def clear():
    """
    Clear the console screen.
    """
    time.sleep(5)
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def execute_sql_statement(query):
    """
    Execute the specified SQL statement in the database.

    Args:
        query (str): The SQL statement to execute.
    """
    with app.app_context():
        try:
            db.session.execute(text(query))
            db.session.commit()
        except Exception:
            pass

def create_tables():
    """
    Create the tables in the database.
    """
    db.create_all()
    db.session.commit()

def create_owner_account(owner_email=OWNER_EMAIL, confirmation_date=SERVER_STARTED_ON):
    """
    Create an owner account with the specified email address and confirmation date.

    Args:
        owner_email (str, optional): The email address of the owner. Defaults to OWNER_EMAIL.
        confirmation_date (datetime, optional): The confirmation date of the owner account. Defaults to SERVER_STARTED_ON.
    """
    if not User.query.filter_by(email_address=owner_email).count():
        owner = User(email_address=owner_email,
                     role="owner",
                     confirmed_on=confirmation_date)
        db.session.add(owner)
    db.session.commit()

def grant_privileges(db_name, db_user):
    """
    Grant all privileges on the specified database to the specified user.

    Args:
        db_name (str): The name of the database.
        db_user (str): The name of the user.
    """
    execute_sql_statement(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")

def create_extension(extension_name="pg_trgm"):
    """
    Create the specified extension in the database.

    Args:
        extension_name (str, optional): The name of the extension. Defaults to "pg_trgm".
    """
    execute_sql_statement(f"CREATE EXTENSION IF NOT EXISTS {extension_name};")

# Automatic scraping

def update_records():
    """
    Updates the records in the database by scraping products from the web.

    This function retrieves all the products from the database and updates their information
    by scraping the web using a spider. If an exception occurs during the scraping process,
    the function continues to the next product.

    Returns:
        None
    """
    urls = list(Product.query.values("url"))
    try:
        spider = MySpider(urls, "list")
        spider.run()
    except ValueError:
        return
