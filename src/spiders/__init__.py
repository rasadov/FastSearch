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
        "https://www.amazon.com/ASUS-Graphics-DisplayPort-Axial-tech-Technology/dp/B0985X2YR1/ref=sr_1_2?dib=eyJ2IjoiMSJ9.LX1K_L7kjN5jfdbS2bz5ISY-0qX-WqbDGhLy_xQRxUa7jNE9GF00nvlNgHLng8OQgyyAdeRhh-wuiheifXq-FpgqfGFIlME0j7MBQySLcFy5uiotTNHcUnTQKlB9kTp-vzSp_BSKR6TB1goI5nLFixowzQoo_Rr7fcHhW_tpYI0Yo5iI9uPi-kjYtyKOT8S__FyNW8GHwHWI2pvyqVXkNSXJ_fkAGtIysVGcjMWS9u0.y7KHAmPc0ciS0TNRf48erYTVHqCuvkYNZkqmFwfZiXE&dib_tag=se&keywords=RTX+3060&qid=1709988872&sr=8-2&ufe=app_do%3Aamzn1.fos.c3015c4a-46bb-44b9-81a4-dc28e6d374b3",
        "url",
    )

    # Run the spider
    spider.run()
