from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider

spider = MySpider("", "url", 5, 10)


spider.run()
