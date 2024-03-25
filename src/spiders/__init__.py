"""
This file imports all the spiders and runs a specific spider.
~~~~~~~~~~~~~~~~~~~~~

Usage:
    python __init__.py

"""

import sys

sys.path.append("src\spiders")

from myproject.myproject.spiders import MySpider

if __name__ == "__main__":
    # Create an instance of MySpider with the desired URL and name
    spider = MySpider(
        "https://www.excaliberpc.com/797109/msi-vector-17-hx-a14vhg-649us.html",
        "url",
    )

    # Run the spider
    spider.run()
