import json
from datetime import datetime

import pandas as pd
import scrapy


class MatchesSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "matches"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)

        # create data frames and safe them only if they not already existing
        # matches_df = pd.DataFrame(
        #     columns=['Match_ID', 'Duration', 'Start_Time', 'Radiant_Team_ID', 'Radiant_Name', 'Dire_Team_ID',
        #              'Dire_Name', 'League_ID', 'League_Name', 'Radiant_Score', 'Dire_Score', 'Radiant_Win', 'Dire_Win'])
        # matches_df.to_csv('../Data/DotaMatches.csv', index=False)
        #
        # team_player_df = pd.DataFrame(
        #     columns=["Team_ID", "Team_Name", "Account_ID", "Account_Name", "Games_Played", "Wins", "Is_Current_Member"])
        # team_player_df.to_csv('../Data/DotaTeamPlayers.csv', index=False)

        # read in the dfs and convert the date column to a pandas datetime column
        self.matches_df = pd.read_csv('../Data/DotaMatches.csv', index_col=False, header=0)
        self.matches_df["Start_Time"] = pd.to_datetime(self.matches_df["Start_Time"])
        self.team_player_df = pd.read_csv('../Data/DotaTeamPlayers.csv', index_col=False, header=0)
        # adjust match id to the newest
        self.match_id = 5253284519

    def start_requests(self):
        """start the data gathering"""
        # match id less than 2040098389 goes down to 2015-12-30
        # start match id is 5441224492
        while self.match_id >= 1840098389:
            url = f"https://api.opendota.com/api/proMatches?less_than_match_id={self.match_id}&sort=%22match_id%22"
            yield scrapy.Request(url=url, callback=self.parse)

        # url = f"https://api.opendota.com/api/proMatches?less_than_match_id={self.match_id}&sort=%22match_id%22"
        # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response_list = json.loads(response.text)
        for res in response_list:
            # check if match is already in the data frame
            if len(self.matches_df[self.matches_df["Match_ID"] == res['match_id']]) > 0 and res[
                'radiant_name'] != 'Unknown Team' and res['dire_name'] != 'Unknown Team':
                continue
            date = datetime.fromtimestamp(res['start_time']).replace(microsecond=0, minute=0, hour=0, second=0)
            data = {'Match_ID': res['match_id'], 'Duration': res['duration'], 'Start_Time': date,
                    'Radiant_Team_ID': res['radiant_team_id'], 'Radiant_Name': res['radiant_name'],
                    'Dire_Team_ID': res['dire_team_id'], 'Dire_Name': res['dire_name'], 'League_ID': res['leagueid'],
                    'League_Name': res['league_name'], 'Radiant_Score': res['radiant_score'],
                    'Dire_Score': res['dire_score'], 'Radiant_Win': 1 if res["radiant_win"] else 0,
                    'Dire_Win': 0 if res["radiant_win"] else 1}
            # merge the result data frame with the current data frame
            data_df = pd.DataFrame(data, index=[len(self.matches_df)])
            frames = [data_df, self.matches_df]
            self.matches_df = pd.concat(frames)
            # if a team is not in the team players data frame then create new entries
            if len(
              self.team_player_df[self.team_player_df["Team_ID"] == data["Radiant_Team_ID"]]) == 0 and 'Unknown Team' != \
              data["Radiant_Name"]:
                yield scrapy.Request(url=f'https://api.opendota.com/api/teams/{data["Radiant_Team_ID"]}/players',
                                     callback=self.parse_team_players,
                                     meta={"Team_ID": data["Radiant_Team_ID"], "Team_Name": data["Radiant_Name"]})
            if len(
              self.team_player_df[self.team_player_df["Team_ID"] == data["Radiant_Team_ID"]]) == 0 and 'Unknown Team' != \
              data["Dire_Name"]:
                yield scrapy.Request(url=f'https://api.opendota.com/api/teams/{data["Dire_Team_ID"]}/players',
                                     callback=self.parse_team_players,
                                     meta={"Team_ID": data["Dire_Team_ID"], "Team_Name": data["Dire_Name"]})
        # save the result data frame
        self.matches_df.to_csv('../Data/DotaMatches.csv', index=False)
        # adjust the match id to the smallest match id in the response which is the last entry since the response is
        # sorted according to the match id
        self.match_id = response_list[len(response_list) - 1]["match_id"]

    def parse_team_players(self, response):
        response_list = json.loads(response.text)
        team_id = response.meta.get('Team_ID')
        team_name = response.meta.get('Team_Name')
        for res in response_list:
            data = {"Team_ID": team_id, "Team_Name": team_name, "Account_ID": res["account_id"],
                    "Account_Name": res["name"],
                    "Games_Played": res["games_played"], "Wins": res["wins"],
                    "Is_Current_Member": res["is_current_team_member"]}
            data_df = pd.DataFrame(data, index=[len(self.matches_df)])
            frames = [data_df, self.team_player_df]
            self.team_player_df = pd.concat(frames)
        self.team_player_df.to_csv('../Data/DotaTeamPlayers.csv', index=False)
