from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider


spider = MySpider("https://www.excaliberpc.com/792006/msi-raider-ge76-12ue-871-17.3.html", 'url', 1,10)


spider.run()
