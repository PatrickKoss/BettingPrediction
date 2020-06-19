import os

import django
import scrapy
from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BettingRestAPI.settings')
django.setup()

from csgo_api.models import Team, Match
from dateutil import parser
from datetime import datetime
import keras
import numpy as np

import tensorflow as tf

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)


class MatchesSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "MatchesSpider"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)

    def start_requests(self):
        """start the data gathering"""
        # this site has all upcoming matches
        yield scrapy.Request(url='https://www.hltv.org/betting/money', callback=self.parse)

    def parse(self, response):
        # get the mode for each match. It is either bo1 or bo3
        modes = response.css('div.b-match-container div.b-best-of::text').extract()
        # for each match we need the exact details which are in a sub page
        team_links = response.css('table.bookmakerMatch tr.teamrow td.bookmakerTeamBox div.team-name a').xpath(
            "@href").extract()
        # make the team links unique since we will have duplicates for each match
        team_links_unique = []
        for link in team_links:
            if link not in team_links_unique:
                team_links_unique.append(link)
        for index, link in enumerate(team_links_unique):
            yield scrapy.Request(url="https://www.hltv.org" + link, callback=self.parse_matches,
                                 meta={"mode": modes[index]})

    def parse_matches(self, response):
        # get the odds
        odds_team1 = response.css('div.team-odds a::text').extract()[0].split("- ")[1]
        odds_team2 = response.css('div.team-odds a::text').extract()[1].split("- ")[1]
        if odds_team1 == "-" or odds_team2 == "-":
            return
        # get the exact match date
        match_time = response.css('div.analytics-info div.event-time span::text').extract()[0]
        match_date = response.css('div.analytics-info div.event-date span::text').extract()[0]
        match_date = parser.parse(match_date).date()
        match_date = datetime.strptime(f"{match_date.day}-{match_date.month}-{match_date.year} {match_time}",
                                       "%d-%m-%Y %H:%M")

        mode = response.meta["mode"]
        team1 = response.css('div.team-name div.name::text').extract()[0]
        team1_model = Team.objects.filter(name=team1)
        # check if the team1 exists in the database
        if team1_model.exists():
            team1_model = team1_model.order_by('-end_date').first()
        else:
            return

        team2 = response.css('div.team-name div.name::text').extract()[1]
        team2_model = Team.objects.filter(name=team2)
        # check if team2 exists in the database
        if team2_model.exists():
            team2_model = team2_model.order_by('-end_date').first()
        else:
            return

        # check if the match is already in the database
        if Match.objects.filter(date=match_date, Team_1__name=team1, Team_2__name=team2).exists():
            return

        # get the correct prediction model for the right mode
        if mode == "BO1":
            prediction_model = keras.models.load_model("../../../csgo_api/PredictionModels/NNModel_allMatchesWins.h5")
        else:
            prediction_model = keras.models.load_model("../../../csgo_api/PredictionModels/NNModel_bestOf3Wins.h5")

        # create the prediction numpy array
        prediction_array = np.array([[team1_model.winning_percentage]])
        prediction_array = np.concatenate((prediction_array,
                                           self.get_team_player_array(team1_model.Player_1, team1_model.Player_2,
                                                                      team1_model.Player_3, team1_model.Player_4,
                                                                      team1_model.Player_5)), axis=1)
        prediction_array = np.concatenate((prediction_array, np.array([[team2_model.winning_percentage]])), axis=1)
        prediction_array = np.concatenate((prediction_array,
                                           self.get_team_player_array(team2_model.Player_1, team2_model.Player_2,
                                                                      team2_model.Player_3, team2_model.Player_4,
                                                                      team2_model.Player_5)), axis=1)
        team_2_confidence = round(prediction_model.predict(prediction_array)[0][0], 3)
        team_1_confidence = round(1 - team_2_confidence, 3)
        team_1_confidence = team_1_confidence.item()
        team_2_confidence = team_2_confidence.item()

        # after all data is gathered, save the data in the database
        model = Match.objects.create(date=match_date, Team_1=team1_model, Team_2=team2_model, odds_team_1=odds_team1,
                                     odds_team_2=odds_team2, team_1_confidence=team_1_confidence,
                                     team_2_confidence=team_2_confidence, mode=mode)
        model.save()

    def get_player_stats_array(self, player):
        return np.array([[player.dpr, player.kast, player.impact, player.adr, player.kpr]])

    def get_team_player_array(self, player1, player2, player3, player4, player5):
        team_player_array = self.get_player_stats_array(player1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player2)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player3)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player4)), axis=1)
        return np.concatenate((team_player_array, self.get_player_stats_array(player5)), axis=1)


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    scheduler.add_job(process.crawl, args=[MatchesSpider])
    scheduler.add_job(process.crawl, 'interval', args=[MatchesSpider], seconds=60*60*12)
    scheduler.start()
    process.start(False)
