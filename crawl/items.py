# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum


class TypeMovie(Enum):
    oddMovies = 1
    suiteMovies = 2


class CrawlItem(scrapy.Item):
    _id = scrapy.Field()
    url_root = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    title_english = scrapy.Field()
    thumbnail = scrapy.Field()
    type = scrapy.Field()
    kind = scrapy.Field()
    duration = scrapy.Field()
    status = scrapy.Field()
    actors = scrapy.Field()
    director = scrapy.Field()
    release_year = scrapy.Field()
    views = scrapy.Field()
    imdb = scrapy.Field()
    description = scrapy.Field()
