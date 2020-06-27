import time
from datetime import datetime, timedelta

import scrapy

from ..items import Team


class PlayerSpider(scrapy.Spider):
    name = "team"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        end = datetime.today()
        start = end - timedelta(days=6 * 30)
        self.date_range_string = f"startDate={start.year}-{start.strftime('%m')}-{start.strftime('%d')}" \
                                 f"&endDate={end.year}-{end.strftime('%m')}-{end.strftime('%d')}"

    def start_requests(self):
        urls = [
            'https://www.hltv.org/stats/teams?'
        ]
        for url in urls:
            url += self.date_range_string
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        player_urls = response.css('table tbody tr td a').xpath("@href").extract()
        for player_url in player_urls:
            player_url = player_url.split("?")[0]
            player_url += "?" + self.date_range_string
            time.sleep(0.5)
            url = response.urljoin(player_url)
            yield scrapy.Request(url, callback=self.parse_teams)

    def parse_teams(self, response):
        item = Team()
        item["name"] = response.css(".context-item-name::text").get()
        summary = response.css(".large-strong::text").extract()
        item["kd"] = summary[5]
        item["wins"] = summary[1].split("/")[0]
        item["losses"] = summary[1].split("/")[-1]
        players = response.css(".text-ellipsis::text").extract()
        item["player_1"] = players[0]
        item["player_2"] = players[1]
        item["player_3"] = players[2]
        item["player_4"] = players[3]
        item["player_5"] = players[4]
        yield item
