from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider

spider = MySpider("https://www.gamestop.com/pc-gaming/pc-components/graphics-cards/products/asus-dual-geforce-rtx-3060-white-oc-edition-8gb-gddr6-graphic-card/20005159.html", "url", 5, 10)


spider.run()
