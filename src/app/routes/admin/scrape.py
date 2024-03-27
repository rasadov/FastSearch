"""
This section contains routes for running the scrapy spider.
- The spider can be runned by entering the URL of the product manually.
- The spider can be runned by entering the query to the search engine.
"""
from models import Product
from web import (app, admin_required, render_template,
                request, redirect, flash, session)
from urllib.parse import urlparse
from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import sys
from flask import jsonify

sys.path.append(r"C:\\Users\\RAUF\\Desktop\\Github_works\\FastSearch\\src")

from spiders import MySpider

# Manual scraping

def run_spider(url, method=None, pages=None, results_per_page=None):
    """
    Runs a spider to scrape data from a given URL.

    Args:
        url (str): The URL to scrape data from.
        method (str, optional): The HTTP method to use for the request. Defaults to None.
        pages (int, optional): The number of pages to scrape. Defaults to None.
        results_per_page (int, optional): The number of results to scrape per page. Defaults to None.

    Returns:
        None
    """
    spider = MySpider(url, method, pages, results_per_page)
    spider.run()


@app.get("/admin/product/scrape")
@admin_required
def admin_scrape_get():
    """
    Renders the 'Admin/Scraping/add.html' template.
    """

    return render_template("Admin/Scraping/add.html")


@app.post("/admin/product/scrape")
@admin_required
def admin_scrape_post():
    """
    Scrapes the product information from the provided URL and adds it to the database.

    This function is a route handler for the '/admin/product/scrape' endpoint. It is triggered when a POST request is made to the endpoint.
    The function first checks the 'source' parameter in the request form to determine the scraping method.

    If the method is 'custom', it retrieves the 'query' parameter from the form and validates it. If the URL is valid, it checks if the product already exists in the database. If it does, it redirects to the product details page. If not, it starts a new process to run the spider for scraping the product information from the URL. After the process completes, it checks if the product was successfully added to the database and redirects accordingly.

    If the method is 'google', it retrieves the 'query', 'pages', and 'results_per_page' parameters from the form. It validates the 'query' parameter and starts a new process to run the spider for scraping the product information from Google search results. After the process completes, it displays a success message and redirects to the product listing page.

    Returns:
        If the product is added successfully, redirects to the product details page.
        If the product already exists in the database, redirects to the existing product details page.
        If the product could not be added, redirects back to the add product page with an error message.

    """

    data = request.get_json()

    method = data.get("source")

    url = data.get("query")
    if not url:
        return jsonify(
            {
                "status": "error", 
                "message": "Please enter a valid URL"
            }
        )

    if method == "custom":
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

        p = Process(target=run_spider, args=(url, "url"))
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
        else:
            return jsonify(
                {
                    "status": "error", 
                    "message": "Product could not be added"
                }
            )

    elif method == "google":
        pages = data.get("pages")
        results_per_page = data.get("results_per_page")

        p = Process(
            target=run_spider, args=(url, "google", int(pages), int(results_per_page))
        )
        p.start()
        p.join()

        return jsonify(
            {
                "status": "success",
                "message": "Products added to database successfully",
            }
        )

# Automatic scraping 
"""
This section contains the code for running the spider automatically at regular intervals.
"""


def update_records():
    """
    Updates the records in the database by scraping products from the web.

    This function retrieves all the products from the database and updates their information
    by scraping the web using a spider. If an exception occurs during the scraping process,
    the function continues to the next product.

    Returns:
        None
    """
    products = Product.query.all()
    for product in products:
        try:
            spider = MySpider(product.url, "url")
            spider.run()
        except Exception:
            continue


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_records, trigger="interval", hours=24)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
