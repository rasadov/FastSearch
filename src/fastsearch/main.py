from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider


spider = MySpider("Rtx 3060 site:amazon.co.uk", 'google', 1,10)


spider.run()
