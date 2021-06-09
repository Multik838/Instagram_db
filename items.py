# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    name_followers = scrapy.Field()
    name_following = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    photo_followers = scrapy.Field()
    photo_following = scrapy.Field()
    like = scrapy.Field()
    post_data = scrapy.Field()
    subscribers = scrapy.Field()
    full_name = scrapy.Field()
    parent_name = scrapy.Field()
    parent_id = scrapy.Field()
    next_max_id = scrapy.Field()
    _id = scrapy.Field()
    pass
# Сюда данные попадают из нашего паука instacom