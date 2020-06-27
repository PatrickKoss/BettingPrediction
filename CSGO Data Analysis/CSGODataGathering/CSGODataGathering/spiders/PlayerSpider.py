import scrapy

from ..items import Player
from datetime import datetime, timedelta
import time


class PlayerSpider(scrapy.Spider):
    name = "player"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        end = datetime.today()
        start = end - timedelta(days=6 * 30)
        self.date_range_string = f"startDate={start.year}-{start.strftime('%m')}-{start.strftime('%d')}" \
                                 f"&endDate={end.year}-{end.strftime('%m')}-{end.strftime('%d')}"

    def start_requests(self):
        urls = [
            'https://www.hltv.org/stats/players?'
        ]
        for url in urls:
            url += self.date_range_string
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        player_urls = response.css('.playerCol a').xpath("@href").extract()
        for player_url in player_urls:
            player_url = player_url.split("?")[0]
            player_url += "?" + self.date_range_string
            time.sleep(2)
            url = response.urljoin(player_url)
            yield scrapy.Request(url, callback=self.parse_players)

    def parse_players(self, response):
        item = Player()
        item["name"] = response.css(".summaryNickname::text").get()
        summary = response.css(".summaryStatBreakdownDataValue::text").extract()
        item["rating"] = summary[0]
        item["dpr"] = summary[1]
        item["kast"] = summary[2]
        item["impact"] = summary[3]
        item["adr"] = summary[4]
        item["kpr"] = summary[5]
        yield item
