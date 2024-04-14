# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MangacrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MhItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mh_title = scrapy.Field()
    mh_url = scrapy.Field()
    mh_chapter_list = scrapy.Field()
    mh_chapter_length = scrapy.Field()


class ChapterItem(scrapy.Item):
    chapter_url = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_time = scrapy.Field()
    chapter_content_url_list = scrapy.Field()
