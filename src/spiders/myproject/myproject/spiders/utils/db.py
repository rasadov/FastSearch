"""
This module contains functions for interacting with the database.

The functions in this module are used to save products to the database or 
update existing products if they already exist.

Functions:
- save_product_to_database(params):
Saves a product to the database or updates an existing product if it already exists.
- create_product(curr, params): 
Inserts a new product into the database with the provided information.
- update_record(curr, result, params): 
Updates an existing record in the database with the provided information.
- deactivate_record(url):
Deactivates a record in the database.
"""

import psycopg2

from app.utils.notifications import notify_price_change

from app import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def save_product_to_database(
    params: dict
) -> None:
    """
    Saves a product to the database or updates an existing product if it already exists.

    Parameters:
    - params (dict): A dictionary containing the product information.

    If the product already exists in the database, the function checks for changes in 
    price, rating, and amount of ratings.
    If the price has changed, it updates the data in the `product` table 
    and saves the price change in the `price_history` table.
    If the rating has changed, it updates the record in the `product` table.
    If the product does not exist in the database, it adds a new record to the `product` table
    and starts tracking the price in the `price_history` table.

    Raises:
    - ValueError: If any of the required params are missing.

    Returns:
    - None
    """

    if (not params.get('url') or not params.get('title') or 
        not params.get('price') or not params.get('price_currency')):
        raise ValueError("Missing required parameters.")

    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    curr = conn.cursor()

    curr.execute(f"""SELECT * FROM product WHERE url = '{params.get('url')}';""")

    result = curr.fetchone()

    curr.execute(
        """
                    CREATE TABLE IF NOT EXISTS price_history (
                    price_history_id SERIAL PRIMARY KEY,
                    product_id INT,
                    price INT NOT NULL,
                    price_currency VARCHAR(255) NOT NULL,
                    change_date DATE NOT NULL,

                    FOREIGN KEY (product_id) REFERENCES product(id)
                    );"""
    )

    # Checking if this record already exists in database
    if result:
        # This product already exists, update the record
        update_record(curr, result, params)
    else:
        # This product does not exist, insert a new record into the database
        create_product(curr, params)

    conn.commit()
    curr.close()
    conn.close()

def create_product(
    curr: psycopg2.extensions.cursor,
    params: dict
) -> None:
    """
    Inserts a new product into the database with the provided information.

    Args:
        curr (psycopg2.extensions.cursor): The database cursor.
        url (str): The URL of the product.
        title (str): The title of the product.
        price (float): The price of the product.
        price_currency (str): The currency of the price.
        rating (float, optional): The rating of the product. Defaults to None.
        amount_of_ratings (int, optional): The amount of ratings for the product. Defaults to None.
        item_class (str, optional): The class of the product. Defaults to None.
        producer (str, optional): The producer of the product. Defaults to None.
        image_url (str, optional): The URL of the product image. Defaults to None.
        availability (str, optional): The availability of the product. Defaults to 'In stock'.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the database operation.

    """
    try:
        curr.execute(
            """
            INSERT INTO product (url, title, price, price_currency, item_class,
            producer, amount_of_ratings, rating, image_url, availability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (params.get('url'), params.get('title'),
             params.get('price'), params.get('price_currency'),
             params.get('item_class'), params.get('producer'),
             params.get('amount_of_ratings)'), params.get('rating'),
             params.get('image_url'), params.get('availability')),
        )
    except Exception as e:
        print(f"An error occurred: {e}")

    curr.execute(f"""SELECT * FROM product WHERE url = '{params.get('url')}';""")

    result = curr.fetchone()

    product_id = result[0]

    curr.execute(
        """
        INSERT INTO price_history (product_id, price, price_currency, change_date)
        VALUES (%s, %s, %s, CURRENT_DATE);
    """,
        (product_id, params.get('price'), params.get('price_currency')),
    )

def update_record(
    curr: psycopg2.extensions.cursor,
    result: tuple,
    params: dict
) -> None:
    """
    Updates an existing record in the database with the provided information.

    Args:
    - curr (psycopg2.extensions.cursor): The database cursor.
    - result (tuple): The record to update.
    - url (str): The URL of the product.
    - title (str): The title of the product.
    - price (float): The price of the product.
    - price_currency (str): The currency of the price.
    - rating (float, optional): The rating of the product. Defaults to None.
    - amount_of_ratings (int, optional): The amount of ratings for the product. Defaults to None.
    - item_class (str, optional): The class of the product. Defaults to None.
    - producer (str, optional): The producer of the product. Defaults to None.
    - image_url (str, optional): The URL of the product image. Defaults to None.
    - availability (str, optional): The availability of the product. Defaults to 'In stock'.

    Returns:
    - None

    Raises:
    - Exception: If an error occurs during the database operation.

    """
    price_in_db = result[3]
    amount_of_rating_in_db = result[6]
    rating_in_db = result[7]

    if (
        price_in_db != params.get('price')
        or rating_in_db != params.get('rating')
        or amount_of_rating_in_db != params.get('amount_of_ratings')
    ):

        # Checking if price of product has changed
        if price_in_db != params.get('price'):

            if price_in_db > params.get('price'):
                notify_price_change(params.get('url'))

            product_id = result[0]

            # Saving price change to keep track of price
            curr.execute(
                """
                INSERT INTO price_history (product_id, price, price_currency, change_date)
                VALUES (%s, %s, %s, CURRENT_DATE);
            """,
                (product_id, params.get('price'), params.get('price_currency')),
            )

        curr.execute(
            """
            UPDATE product
            SET price = %s, price_currency = %s, title = %s, item_class = %s, producer = %s,
            amount_of_ratings = %s, rating = %s, image_url = %s, availability = %s
            WHERE url = %s;
        """,
            (
            params.get('price'),
            params.get('price_currency'),
            params.get('title'),
            params.get('item_class'),
            params.get('producer'),
            params.get('amount_of_ratings'),
            params.get('rating'),
            params.get('image_url'),
            params.get('availability'),
            params.get('url'),
            ),
        )


def deactivate_product(url: str) -> None:
    """
    Deactivates a record in the database.

    Parameters:
    - url (str): The URL of the product to deactivate.

    This function deactivates a record in the `product` table by 
    setting the `active` column to False.
    """
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    curr = conn.cursor()

    curr.execute(f"""
                 UPDATE product SET availability = 'Out of stock' WHERE url = '{url}';
                 """)

    conn.commit()
    curr.close()
    conn.close()
