import json
from datetime import datetime

import pandas as pd
import scrapy


class PlayerSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "player"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)
        # create player data frame
        player_df = pd.DataFrame(
            columns=['Account_ID', 'Name', 'Country_Code', 'Team_ID', 'Team_Name', 'Team_Tag', 'Date'])
        player_df.to_csv('../Data/DotaPlayer.csv', index=False)

        # read in the dfs and convert the date column to a pandas datetime column
        self.player_df = pd.read_csv('../Data/DotaPlayer.csv', index_col=False, header=0)
        self.player_df["Date"] = pd.to_datetime(self.player_df["Date"])

    def start_requests(self):
        """start the data gathering"""
        # first gather all pro players
        yield scrapy.Request(url='https://api.opendota.com/api/proPlayers', callback=self.parse)

    def parse(self, response):
        """the response are all pro players. This method saves these players in a data frame"""
        response_list = json.loads(response.text)
        for res in response_list:
            date = datetime.now().replace(second=0, microsecond=0, hour=0, minute=0)
            data = {'Account_ID': res['account_id'], 'Name': res['name'], 'Country_Code': res['country_code'],
                    'Team_ID': res['team_id'], 'Team_Name': res['team_name'], 'Team_Tag': res['team_tag'], 'Date': date}
            # merge the result data frame with the current data frame
            data_df = pd.DataFrame(data, index=[len(self.player_df)])
            frames = [data_df, self.player_df]
            self.player_df = pd.concat(frames)
        # save the result data frame
        self.player_df.to_csv('../Data/DotaPlayer.csv', index=False)
