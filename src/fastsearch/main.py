from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider


# spider = MySpider("https://www.newegg.com/asus-geforce-rtx-3060-dual-rtx3060-o12g-white/p/14-126-634", 'url')


# spider.run()


spider = MySpider("https://www.newegg.com/asus-geforce-rtx-3060-dual-rtx3060-o12g-white/p/14-126-634", 'url')


spider.run()
