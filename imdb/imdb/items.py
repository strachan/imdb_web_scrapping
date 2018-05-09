# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ImdbItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    imdb_score = Field()
    metascore = Field()
    genres = Field()
    country = Field()
    release_date = Field()
    budget = Field()
    opening_usa = Field()
    usa_gross = Field()
    worldwide_gross = Field()
    production_companies = Field()
