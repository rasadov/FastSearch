from utils import *
import requests
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider
import time


spider = MySpider("https://www.ebay.com/itm/355363099516", 'url', 1,10)


spider.run()
