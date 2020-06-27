# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CsgodatagatheringItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Player(scrapy.Item):
    name = scrapy.Field()
    rating = scrapy.Field()
    # deaths per round
    dpr = scrapy.Field()
    # percentage of rounds in which the player either had a kill, assist, survived or was traded
    kast = scrapy.Field()
    # measures the impact made from multikills, opening kills, and clutches
    impact = scrapy.Field()
    # average damage per round
    adr = scrapy.Field()
    # kills per round
    kpr = scrapy.Field()


class Team(scrapy.Item):
    name = scrapy.Field()
    kd = scrapy.Field()
    wins = scrapy.Field()
    losses = scrapy.Field()
    player_1 = scrapy.Field()
    player_2 = scrapy.Field()
    player_3 = scrapy.Field()
    player_4 = scrapy.Field()
    player_5 = scrapy.Field()


class Match(scrapy.Item):
    team_1 = scrapy.Field()
    team_2 = scrapy.Field()
    win_team_1 = scrapy.Field()
    win_team_2 = scrapy.Field()
    map = scrapy.Field()
