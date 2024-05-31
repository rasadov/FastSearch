"""
This file contains the implementation of manual and automated web scraping functionality.
~~~~~~~~~~~~~~~~~~~~~

Manual Scraping:
----------------
The manual scraping functionality allows users to scrape product information from a given URL
and add it to the database. The scraping process is triggered by making a POST request to the
'/admin/product/scrape' endpoint. The scraping method can be either 'custom' or 'google'.

- If the method is 'custom', the URL is retrieved from the request form.
The URL is validated and checked against the existing products in the database.
If the product already exists, the user is redirected to the product details page. 
If not, a new process is started to run the spider for scraping
the product information from the URL.
After the process completes, the product is checked
if it was successfully added to the database and the user is redirected accordingly.

- If the method is 'google', the `query` and `pages` parameters are retrieved from the request form.
The query parameter is validated and a new process is started to run the spider
for scraping the product information from Google search results.
After the process completes, a success message is displayed and
the user is redirected to the product listing page.

Automated Scraping:
-------------------
The automated scraping functionality runs the spider automatically
at regular intervals to update the records in the database. 
This is achieved using the apscheduler library.
The spider retrieves all the products from the database and
updates their information by scraping the web.
If an exception occurs during the scraping process, the function continues to the next product.
The spider is scheduled to run every 24 hours.

Note: The code in this file assumes the presence of other modules and packages
such as 'models', 'web', 'spiders', etc., which are not included in this code snippet.

"""

import atexit
from urllib.parse import urlparse
from multiprocessing import Process

from apscheduler.schedulers.background import BackgroundScheduler
from flask import request, jsonify, render_template
from flask_login import current_user

from app import app, admin_required, OWNER_EMAIL
from app.models import Product
from spiders import MySpider
from app.utils.email import send_email

# Manual scraping

def run_spider(url, method=None, pages=None):
    """
    Runs a spider to scrape data from a given URL.

    Args:
        url (str): The URL to scrape data from.
        method (str, optional): The HTTP method to use for the request. Defaults to None.
        pages (int, optional): The number of pages to scrape. Defaults to None.

    Returns:
        None
    """
    spider = MySpider(url, method, pages)
    spider.run()


@app.get("/admin/product/scrape")
@admin_required
def admin_scrape_get():
    """
    Renders the 'Admin/scrape.html' template.
    """

    return render_template("Admin/scrape.html")


@app.post("/admin/product/scrape")
def admin_scrape_post():
    """
    Scrapes the product information from the provided URL and adds it to the database.

    This function is a route handler for the '/admin/product/scrape' endpoint.
    It is triggered when a POST request is made to the endpoint.
    The function first checks the 'source' parameter in the request form
    to determine the scraping method.

    If the method is 'custom', it retrieves the 'query' parameter from the form and validates it.
    If the URL is valid, it checks if the product already exists in the database.
    If it does, it redirects to the product details page.
    If not, it starts a new process to run the spider for scraping the product information
    from the URL.
    After the process completes, it checks if the product was successfully
    added to the database and redirects accordingly.

    If the method is 'google', it retrieves the 'query' and 'pages' parameters from the form. 
    It validates the 'query' parameter and starts a new process to run the spider for scraping
    the product information from Google search results. 
    After the process completes, it displays a success message and
    redirects to the product listing page.

    Returns:
        If the product is added successfully, 
        redirects to the product details page.
        If the product already exists in the database, 
        redirects to the existing product details page.
        If the product could not be added, 
        redirects back to the add product page with an error message.

    """

    if current_user.is_anonymous:
        return jsonify(
            {
                "status": "error",
                "message": "You have been logged out, please log in again to continue."
            }
        )

    data: dict = request.get_json()

    method = data.get("source")

    queryList = data.get("query")
    pages = data.get("pages")
    if len(queryList) > 0:
        if method == "custom":
            scrape_url(queryList)
        if method == "google":
            print("queryList: ", queryList)
            scrape_google_query(queryList, pages)

    return jsonify(
        {
            "status": "error",
            "message": "There was some error, make sure you have entered correct parameters."
        }
    )

def scrape_url(url: list):
    """
    Scrapes the given URL and adds the product to the database if it doesn't already exist.

    Args:
        url (list): The URL to scrape.

    Returns:
        dict: A JSON response containing the status and message.

    """
    try:
        url = url[0]
    except IndexError:
        return jsonify(
            {
                "status": "error",
                "message": "URL not provided"
            }
        )
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    product = Product.query.filter_by(url=url)
    if product.count():
        return jsonify(
            {
                "status": "error",
                "message": "Product already exists"
            }
        )

    p = Process(
        target=run_spider,
        args=(url, "url")
        )
    p.start()
    p.join()

    product = Product.query.filter_by(url=url)
    if product.count():
        product = product.first()
        return jsonify(
            {
                "status": "success",
                "message": "Product added successfully"
            }
        )
    return jsonify(
        {
            "status": "error",
            "message": "Product could not be added"
        }
    )

def scrape_google_query(query: list, pages: int):
    """
    Scrapes Google search results for a given query.

    Args:
        query (str): The search query to scrape.
        pages (int): The number of pages to scrape.

    Returns:
        dict: A JSON response containing the status and message.
            - status (str): The status of the scraping process.
            - message (str): A message indicating the success of the operation.
    """
    p = Process(
        target=run_spider,
        args=(query, "google", int(pages))
    )
    p.start()
    p.join()

    return jsonify(
        {
            "status": "success",
            "message": "Products added to database successfully",
        }
    )

def update_records():
    """
    Updates the records in the database by scraping products from the web.

    This function retrieves all the products from the database and updates their information
    by scraping the web using a spider. If an exception occurs during the scraping process,
    the function continues to the next product.

    Returns:
        None
    """
    send_email(OWNER_EMAIL, "The records in the database have been updated.", "Records Updated", "Abyssara")
    try:
        product_links = list(Product.query.values("url"))
        spider = MySpider(product_links, "list")
        spider.run()
    except ValueError:
        return

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_records, trigger="interval", hours=24)
scheduler.start()

atexit.register(scheduler.shutdown)
