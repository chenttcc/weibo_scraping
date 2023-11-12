# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboscrapyItem(scrapy.Item):

    # define the fields for your item here like:
    # the time the scrapying code running
    spidertime = scrapy.Field()
    
    user_link = scrapy.Field()
    user_name = scrapy.Field()
    content = scrapy.Field()
    sendtime = scrapy.Field()

