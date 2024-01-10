from utils import *
import requests
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider
import time


spider = MySpider("rtx 3060 site:amazon.com", 1)
spider.query = "rtx 3060 site:amazon.com"
spider.pages = 1

spider.run()
