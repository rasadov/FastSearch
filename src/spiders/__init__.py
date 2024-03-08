"""This is file imports all the spiders"""

from myproject.myproject.spiders import *
from scrapy import *



if __name__ == "__main__":
    spider = MySpider("", "url")
    # spider.run()
