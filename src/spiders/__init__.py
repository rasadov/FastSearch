"""
This file imports all the spiders.
~~~~~~~~~~~~~~~~~~~~~

Usage:
    python __init__.py

"""

from spiders.myproject.myproject.spiders import MySpider

if __name__ == "__main__":
    # Create an instance of MySpider with the desired URL and name
    spider = MySpider(input("Enter the URL of the product: "), "url")

    # Run the spider
    spider.run()
