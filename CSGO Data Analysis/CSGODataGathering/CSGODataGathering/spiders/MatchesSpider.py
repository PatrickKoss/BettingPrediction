import operator
from datetime import datetime, timedelta

import pandas as pd
import scrapy


class MatchesSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "matches"
    rotate_user_agent = True

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)
        self.date_ranges = []
        start_date = datetime.strptime("2020-05-24", "%Y-%m-%d")
        # every team and player has a date range of 3 months. This list include a list of start and end dates every 3
        # months
        for x in range(0, 30 * 70, 90):
            end_date = start_date.replace(second=0, microsecond=0, hour=0, minute=0)
            start = end_date - timedelta(days=90)
            self.date_ranges.append({'start_date': start, 'end_date': end_date})
            start_date = start.replace(second=0)

        # create data frames and safe them only if they not already existing
        # matches_df = pd.DataFrame(columns=['Date', 'Team1', 'Team2', 'Map', 'Team1_Win', 'Team2_Win'])
        # team_df = pd.DataFrame(columns=['Name', 'KD', 'Wins', 'Losses', 'Winning_Percentage',
        #                                 'Player_1', 'Player_2', 'Player_3',
        #                                 'Player_4', 'Player_5', 'Start_Date', 'End_Date'])
        # player_df = pd.DataFrame(
        #     columns=['Name', 'Rating', 'DPR', 'Kast', 'Impact', 'ADR', 'KPR', 'Start_Date', 'End_Date'])
        # matches_df.to_csv('../Data/Matches.csv', index=False)
        # team_df.to_csv('../Data/Team.csv', index=False)
        # player_df.to_csv('../Data/Player.csv', index=False)

        # read in the dfs and convert the date column to a pandas datetime column
        self.matches_df = pd.read_csv('../Data/Matches.csv', index_col=False, header=0)
        self.matches_df["Date"] = pd.to_datetime(self.matches_df["Date"])
        self.team_df = pd.read_csv('../Data/Team.csv', index_col=False, header=0)
        self.team_df["Start_Date"] = pd.to_datetime(self.team_df["Start_Date"])
        self.team_df["End_Date"] = pd.to_datetime(self.team_df["End_Date"])
        self.player_df = pd.read_csv('../Data/Player.csv', index_col=False, header=0)
        self.player_df["Start_Date"] = pd.to_datetime(self.player_df["Start_Date"])
        self.player_df["End_Date"] = pd.to_datetime(self.player_df["End_Date"])

    def start_requests(self):
        """start the data gathering"""
        urls = []
        # every page has 50 entries of matches so we set the offset to %50
        for i in range(30000, 60000, 50):
            urls.append('https://www.hltv.org/stats/matches?startDate=all&offset={}'.format(i))
        # for each page which include 50 matches we get the data of it and fill the matches
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """this method fill the matches.csv"""
        # get all dates
        dates = response.css('table tbody tr td.date-col a div::text').extract()
        # get all teams as string
        all_teams = response.css('table tbody tr td.team-col a::text').extract()
        # get all links from all teams
        links_teams = response.css('table tbody tr td.team-col a').xpath("@href").extract()
        # this will be a dictionary with teams as keys and links as values to get unique teams
        all_teams_links = {}
        # get all scores
        all_scores = response.css('table tbody tr td.team-col span::text').extract()
        # reformat all teams and scores
        teams_1 = []
        teams_2 = []
        scores_team1 = []
        scores_team2 = []
        for i in range(len(all_teams)):
            # if a team is not in the dict then add it
            if all_teams[i] not in all_teams_links:
                all_teams_links.update({all_teams[i]: links_teams[i]})
            # all even numbers and scores are the first team
            if i % 2 == 0:
                teams_1.append(all_teams[i])
                # scores need to be reformat because they are in the format ( 50) and we need the number
                scores_team1.append(int(all_scores[i].split("(")[1].split(')')[0]))
            # all odd numbers and scores are the second team
            else:
                teams_2.append(all_teams[i])
                scores_team2.append(int(all_scores[i].split("(")[1].split(')')[0]))
        # get all maps
        maps = response.css('table tbody tr td.statsDetail div.dynamic-map-name-full::text').extract()
        # fill the data frame with the data. This is a set with the length of the offset which is 50.
        # so we have 50 values for each list and add them to the data frame
        for date, team1, team2, score1, score2, map in zip(dates, teams_1, teams_2, scores_team1, scores_team2, maps):
            d = date.split('/')
            # check if row already exists in matches data frame
            filtered_match_df = self.matches_df[
                (self.matches_df["Date"].dt.date <= pd.to_datetime(f"20{d[2]}-{d[1]}-{d[0]}")) &
                (self.matches_df["Date"].dt.date >= pd.to_datetime(f"20{d[2]}-{d[1]}-{d[0]}")) &
                (self.matches_df["Team1"] == team1) &
                (self.matches_df["Team2"] == team2) &
                (self.matches_df["Map"] == map)]
            if len(filtered_match_df) > 0:
                continue
            # create a dict with the values for the data frame
            data = {'Date': pd.to_datetime(f"20{d[2]}-{d[1]}-{d[0]}"), 'Team1': team1, 'Team2': team2,
                    'Map': map, 'Team1_Win': 1 if score1 > score2 else 0, 'Team2_Win': 1 if score1 < score2 else 0}
            # merge the result data frame with the current data frame
            data_df = pd.DataFrame(data, index=[len(self.matches_df)])
            frames = [data_df, self.matches_df]
            self.matches_df = pd.concat(frames)
            # save the result data frame
            self.matches_df.to_csv('../Data/Matches.csv', index=False)

            # next we want to add teams to the teams data frame. If the team with a specific date range is not in the
            # data frame of teams then add this team
            filtered_team_df = self.team_df[
                (self.team_df["Name"] == team1) & (
                  self.team_df["Start_Date"] <= data["Date"]) & (data["Date"] <= self.team_df["End_Date"])
                ]
            if len(filtered_team_df) == 0:
                yield scrapy.Request(self.get_link_team(team1, all_teams_links, data["Date"]),
                                     callback=self.parse_teams)

            # do the same for the second team
            filtered_team_df = self.team_df[
                (self.team_df["Name"] == team2) & (
                  self.team_df["Start_Date"] <= data["Date"]) & (data["Date"] <= self.team_df["End_Date"])
                ]
            if len(filtered_team_df) == 0:
                yield scrapy.Request(self.get_link_team(team2, all_teams_links, data["Date"]),
                                     callback=self.parse_teams)

    def get_link_team(self, team, all_teams_links, date):
        """returns the link for a team on a specific date range"""
        filtered_date = list(filter(
            lambda el: el["start_date"] <= date <= el["end_date"], self.date_ranges))[0]
        return "https://www.hltv.org" + all_teams_links[team].split("?")[
            0] + f"?startDate={filtered_date['start_date'].year}-" \
                 f"{filtered_date['start_date'].strftime('%m')}-" \
                 f"{filtered_date['start_date'].strftime('%d')}" \
                 f"&endDate={filtered_date['end_date'].year}-" \
                 f"{filtered_date['end_date'].strftime('%m')}-" \
                 f"{filtered_date['end_date'].strftime('%d')}"

    def parse_teams(self, response):
        """this method fill the team.csv"""
        # get the date range from the passed parameters in the header
        start_date, end_date = self.get_dates_from_response(response)
        # get player names, links, and played maps
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

        # fill a team dict to merge it with the result data frame
        summary = response.css(".large-strong::text").extract()
        team_dict = {'Name': response.css(".context-item-name::text").get(),
                     'KD': summary[5],
                     'Wins': int(summary[1].split("/")[0]),
                     'Losses': int(summary[1].split("/")[-1]),
                     'Winning_Percentage': int(summary[1].split("/")[0]) / (
                       int(summary[1].split("/")[0]) + int(summary[1].split("/")[-1])),
                     'Player_1': players_dicts[0]["name"],
                     'Player_2': players_dicts[1]["name"],
                     'Player_3': players_dicts[2]["name"],
                     'Player_4': players_dicts[3]["name"],
                     'Player_5': players_dicts[4]["name"],
                     'Start_Date': pd.to_datetime(start_date),
                     'End_Date': pd.to_datetime(end_date)}
        # merge the result data frame with the current data frame
        data_df = pd.DataFrame(team_dict, index=[len(self.team_df)])
        frames = [data_df, self.team_df]
        self.team_df = pd.concat(frames)
        # save the result data frame
        self.team_df.to_csv('../Data/Team.csv', index=False)

        # next add players for the current date range
        for i in range(0, 5, 1):
            # if the player is not in the data frame then add him
            filtered_players_df = self.player_df[
                (self.player_df["Name"] == players_dicts[i]["name"]) & (self.player_df["Start_Date"] <= start_date)
                & (end_date <= self.player_df["End_Date"])
                ]
            if len(filtered_players_df) == 0:
                yield scrapy.Request("https://www.hltv.org" + players_dicts[i]["link"], callback=self.parse_players)

    def parse_players(self, response):
        """this method fill players in the player.csv"""
        # get date range from the header params of the response
        start_date, end_date = self.get_dates_from_response(response)
        # fill the player dict with his data
        summary = response.css(".summaryStatBreakdownDataValue::text").extract()
        player_dict = {"Name": response.css(".summaryNickname::text").get(),
                       "Rating": summary[0],
                       "DPR": summary[1],
                       "Kast": summary[2],
                       "Impact": summary[3],
                       "ADR": summary[4],
                       "KPR": summary[5],
                       "Start_Date": pd.to_datetime(start_date),
                       "End_Date": pd.to_datetime(end_date)}
        # merge the result data frame with the current data frame
        data_df = pd.DataFrame(player_dict, index=[len(self.player_df)])
        frames = [data_df, self.player_df]
        self.player_df = pd.concat(frames)
        # save the result data frame
        self.player_df.to_csv('../Data/Player.csv', index=False)

    def get_dates_from_response(self, response):
        """this method returns the start date and end date as datetime object from a response"""
        params_string = response.url.split("?")[-1]
        params_string = params_string.split("&")
        start_date = params_string[0].split("=")[-1]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = params_string[1].split("=")[-1]
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        return start_date, end_date
