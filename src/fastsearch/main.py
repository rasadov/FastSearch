from utils import *
from scrapy import *
from myproject.myproject.spiders.myspider import MySpider

spider = MySpider("https://www.gamestop.com/pc-gaming/pc-components/graphics-cards/products/pny-geforce-rtx-3060-12gb-xlr8-gaming-revel-epic-x-rgb-single-fan-graphics-card-gmr3061n4jcet1bktp-brown-box/11185352.html", "url", 5, 10)


spider.run()
