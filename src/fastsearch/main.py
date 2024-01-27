from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider

spider = MySpider("https://www.gamestop.com/pc-gaming/pc-components/graphics-cards/products/asus-gaming-rtx-3060-ti-oc-edition-8g-gddr6x-graphic-card/393863.html", "url", 5, 10)


spider.run()
