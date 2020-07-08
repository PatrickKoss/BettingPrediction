import operator
import os
from datetime import datetime, timedelta

import django
import scrapy
from apscheduler.schedulers.twisted import TwistedScheduler
from dateutil import parser
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BettingRestAPI.settings')
django.setup()

from csgo_api.models import Player, Match, MatchResult, Team
import tensorflow as tf

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)


class StatsSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "StatsSpider"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)
        self.team_players = {}

    def start_requests(self):
        """start the data gathering"""
        urls = []
        # every page has 50 entries of matches so we set the offset to 50
        for i in range(0, 200, 100):
            urls.append('https://www.hltv.org/results?offset={}'.format(i))
        # for each page which include 50 matches we get the data of it and fill the matches
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # get team names and links
        team_name_1 = response.css(
            'div.results-all div.result-con div.result td.team-cell div.team1 div.team::text').extract()
        team_name_2 = response.css(
            'div.results-all div.result-con div.result td.team-cell div.team2 div.team::text').extract()
        match_links = response.css('div.results div.results-all div.results-sublist a').xpath(
            "@href").extract()

        # create final data structure
        result = []
        for team1, team2, link in zip(team_name_1, team_name_2, match_links):
            if not any(d.get("link", None) == link for d in result):
                result.append({"team1_name": team1, "team2_name": team2, "link": link})

        for r in result:
            yield scrapy.Request(url="https://www.hltv.org" + r["link"], callback=self.parse_match,
                                 meta={"ttm": r})

    def parse_match(self, response):
        ttm = response.meta["ttm"]

        # get the exact match date
        match_time = response.css('div.match-page div.time::text').extract()[0]
        match_date = response.css('div.match-page div.date::text').extract()[0]
        match_date = parser.parse(match_date).date()
        match_date = datetime.strptime(f"{match_date.day}-{match_date.month}-{match_date.year} {match_time}",
                                       "%d-%m-%Y %H:%M")

        # get team wins
        team1_score = response.css('div.team1-gradient div::text').extract()[1]
        team2_score = response.css('div.team2-gradient div::text').extract()[1]
        team1_win = 1 if team1_score > team2_score else 0
        team2_win = 1 if team2_score >= team1_score else 0

        match = Match.objects.filter(date=match_date, Team_1__name=ttm["team1_name"],
                                     Team_2__name=ttm["team2_name"])
        # check if the match prediction exists
        if match.exists():
            match = match.first()
            # check if match result not exists
            if not MatchResult.objects.filter(date=match_date, Team_1__name=ttm["team1_name"],
                                              Team_2__name=ttm["team2_name"]).exists():
                model = MatchResult.objects.create(date=match.date, Team_1=match.Team_1, Team_2=match.Team_2,
                                                   team_1_win=team1_win, team_2_win=team2_win)
                model.save()

        # get team links
        today = datetime.now()
        past_3_months = today - timedelta(days=90)
        start_date = f"{past_3_months.year}-{past_3_months.strftime('%m')}-{past_3_months.strftime('%d')}"
        end_date = f"{today.year}-{today.strftime('%m')}-{today.strftime('%d')}"
        team1_link = "/stats" + response.css('div.team1-gradient a').xpath("@href").extract()[
            0] + f"?startDate={start_date}&endDate={end_date}"
        team1_link = team1_link.replace("team", "teams")
        team2_link = "/stats" + response.css('div.team2-gradient a').xpath("@href").extract()[
            0] + f"?startDate={start_date}&endDate={end_date}"
        team2_link = team2_link.replace("team", "teams")
        ttm.update({"team1_link": team1_link, "team2_link": team2_link})

        # check if team needs to be recreated if the team is older than 2 weeks
        past_month_date = datetime.now() - timedelta(days=7)
        # check if team is in db. If not create the team
        team_1 = Team.objects.filter(name=ttm["team1_name"])
        if not team_1.exists():
            yield scrapy.Request(url="https://www.hltv.org" + ttm["team1_link"], callback=self.parse_team)
        else:
            team_1 = team_1.order_by('-end_date').first()
            if team_1.end_date.date() < past_month_date.date():
                yield scrapy.Request(url="https://www.hltv.org" + ttm["team1_link"], callback=self.parse_team)

        team_2 = Team.objects.filter(name=ttm["team2_name"])
        if not team_2.exists():
            yield scrapy.Request(url="https://www.hltv.org" + ttm["team2_link"], callback=self.parse_team)
        else:
            team_2 = team_2.order_by('-end_date').first()
            if team_2.end_date.date() < past_month_date.date():
                yield scrapy.Request(url="https://www.hltv.org" + ttm["team2_link"], callback=self.parse_team)

    def parse_team(self, response):
        # get start and end date
        start_date, end_date = self.get_dates_from_response(response)
        # get winning percentage
        wins_losses = response.css(".large-strong::text").extract()
        winning_percentage = int(wins_losses[1].split("/")[0]) / ((
                                                                    int(wins_losses[1].split("/")[0]) + int(
                                                                      wins_losses[1].split("/")[-1])) if int(
            wins_losses[1].split("/")[0]) + int(wins_losses[1].split("/")[-1]) > 0 else 1)
        winning_percentage = round(winning_percentage, 2)

        # create players of the team
        players_name = response.css('div.teammate div.text-ellipsis::text').extract()
        players_links = response.css('div.reset-grid div.teammate div.teammate-info a').xpath("@href").extract()
        players_links = [link for link in players_links if "/teams/" not in link]
        players_maps = response.css('div.teammate span::text').extract()
        # create a list of dicts to get top 5 players of the team which have played the most maps
        # we define the team by the players who played most maps during the given date range
        players_dicts = []
        for name, map in zip(players_name, players_maps):
            link_outer = ""
            for link in players_links:
                if name in link:
                    link_outer = link
            players_dicts.append({"name": name, "link": link_outer, "map": int(map.split(" maps")[0])})
        # sort the list of dicts according to played maps
        players_dicts.sort(key=operator.itemgetter('map'), reverse=True)

        # sample all data
        team_dict = {'Name': response.css(".context-item-name::text").get(),
                     'Winning_Percentage': winning_percentage,
                     'Player_1': players_dicts[0]["name"],
                     'Player_2': players_dicts[1]["name"],
                     'Player_3': players_dicts[2]["name"],
                     'Player_4': players_dicts[3]["name"],
                     'Player_5': players_dicts[4]["name"],
                     'Start_Date': start_date,
                     'End_Date': end_date}

        # next add players for the current date range
        for i in range(0, 5, 1):
            yield scrapy.Request("https://www.hltv.org" + players_dicts[i]["link"], callback=self.parse_players,
                                 meta={"team_dict": team_dict})

    def parse_players(self, response):
        # get passed team dict
        team_dict = response.meta["team_dict"]
        # get date range from the header params of the response
        start_date, end_date = self.get_dates_from_response(response)
        # fill the player dict with his data
        summary = response.css(".summaryStatBreakdownDataValue::text").extract()
        player_dict = {"Name": response.css(".summaryNickname::text").get(),
                       "DPR": float(summary[1]),
                       "Kast": summary[2],
                       "Impact": float(summary[3]),
                       "ADR": float(summary[4]),
                       "KPR": float(summary[5]),
                       "Start_Date": start_date,
                       "End_Date": end_date}
        # convert kast string into percent float value
        player_dict["Kast"] = player_dict.get("Kast").strip("%")
        if player_dict["Kast"] == "-":
            player_dict["Kast"] = 0
        player_dict["Kast"] = float(player_dict["Kast"])
        player_dict["Kast"] = round(0.01 * player_dict["Kast"], 3)
        # fill a teams dict with its players for the creating process in the database
        if team_dict["Name"] in self.team_players:
            team_players = self.team_players[team_dict["Name"]]
            team_players.append(player_dict)
            self.team_players.update({team_dict["Name"]: team_players})
        else:
            self.team_players.update({team_dict["Name"]: [player_dict]})

        # once a team has 5 players, start the creating process in the db
        if len(self.team_players[team_dict["Name"]]) == 5:
            for player in self.team_players[team_dict["Name"]]:
                # check if player already exists in the database
                if not Player.objects.filter(start_date=player["Start_Date"], end_date=player["End_Date"],
                                             name=player["Name"]).exists():
                    model = Player.objects.create(start_date=player["Start_Date"], end_date=player["End_Date"],
                                                  name=player["Name"], adr=player["ADR"], dpr=player["DPR"],
                                                  kast=player["Kast"], impact=player["Impact"], kpr=player["KPR"])
                    model.save()

            # check if team already exists. If not create it
            if not Team.objects.filter(name=team_dict["Name"], start_date=team_dict["Start_Date"],
                                       end_date=team_dict["End_Date"]).exists():
                # get all players of the team and check if the players exist in the database
                check = True
                player_1 = Player.objects.filter(name=team_dict["Player_1"], start_date=team_dict["Start_Date"],
                                                 end_date=team_dict["End_Date"])
                player_2 = Player.objects.filter(name=team_dict["Player_2"], start_date=team_dict["Start_Date"],
                                                 end_date=team_dict["End_Date"])
                player_3 = Player.objects.filter(name=team_dict["Player_3"], start_date=team_dict["Start_Date"],
                                                 end_date=team_dict["End_Date"])
                player_4 = Player.objects.filter(name=team_dict["Player_4"], start_date=team_dict["Start_Date"],
                                                 end_date=team_dict["End_Date"])
                player_5 = Player.objects.filter(name=team_dict["Player_5"], start_date=team_dict["Start_Date"],
                                                 end_date=team_dict["End_Date"])

                if player_1.exists() and player_2.exists() and player_3.exists() and player_4.exists() and player_5.exists():
                    player_1 = player_1.first()
                    player_2 = player_2.first()
                    player_3 = player_3.first()
                    player_4 = player_4.first()
                    player_5 = player_5.first()
                else:
                    check = False
                # if all players exists then create the team
                if check:
                    team_model = Team.objects.create(name=team_dict["Name"], start_date=team_dict["Start_Date"],
                                                     end_date=team_dict["End_Date"], Player_1=player_1,
                                                     Player_2=player_2, Player_3=player_3,
                                                     Player_4=player_4, Player_5=player_5,
                                                     winning_percentage=team_dict["Winning_Percentage"])
                    team_model.save()

    def get_dates_from_response(self, response):
        """this method returns the start date and end date as datetime object from a response"""
        params_string = response.url.split("?")[-1]
        params_string = params_string.split("&")
        start_date = params_string[0].split("=")[-1]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = params_string[1].split("=")[-1]
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        return start_date, end_date


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    scheduler.add_job(process.crawl, args=[StatsSpider])
    scheduler.add_job(process.crawl, 'interval', args=[StatsSpider], seconds=60 * 60 * 24)
    scheduler.start()
    process.start(False)
