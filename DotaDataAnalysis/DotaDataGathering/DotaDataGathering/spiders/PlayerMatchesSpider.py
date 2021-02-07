import json
from datetime import datetime
import os

import pandas as pd
import scrapy


class PlayerSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "playerMatches"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)
        # read in the dfs and convert the date column to a pandas datetime column
        self.player_df = pd.read_csv('../Data/DotaPlayer.csv', index_col=False, header=0)
        self.player_df["Date"] = pd.to_datetime(self.player_df["Date"])

    def start_requests(self):
        """start the data gathering"""
        urls = []
        for _, row in self.player_df.iterrows():
            urls.append({"url": f"https://api.opendota.com/api/players/{row['Account_ID']}/matches",
                         "Account_ID": row["Account_ID"]})

        for url in urls:
            # check if file already exists and if not create it
            if not any(url["Account_ID"] in s for s in os.listdir("../Data/PlayerMatches")):
                yield scrapy.Request(url=url["url"], callback=self.parse, meta={"Account_ID": url["Account_ID"]})

    def parse(self, response):
        """the response are all matches of a account. This method saves all matches of an account in a csv"""
        response_list = json.loads(response.text)
        account_id = response.meta.get("Account_ID")
        player_matches_df = pd.DataFrame(
            columns=["Match_ID", "Player_Slot", "Radiant_Win", "Duration", "Game_Mode", "Lobby_Type", "Hero_ID",
                     "Start_Time", "Version", "Kills", "Deaths", "Skill", "Leaver_Status", "Party_Size"])
        for res in response_list:
            date = datetime.fromtimestamp(res['start_time']).replace(microsecond=0, minute=0, hour=0, second=0)
            data = {'Match_ID': res["match_id"], "Player_Slot": res["player_slot"], "Radiant_Win": res["radiant_win"],
                    "Duration": res["duration"], "Game_Mode": res["game_mode"], "Lobby_Type": res["lobby_type"],
                    "Hero_ID": res["hero_id"], "Start_Time": date, "Version": res["version"],
                    "Kills": res["kills"], "Deaths": res["deaths"], "Leaver_Status": res["leaver_status"],
                    "Party_Size": res["party_size"]}
            # merge the result data frame with the current data frame
            data_df = pd.DataFrame(data, index=[len(player_matches_df)])
            frames = [data_df, player_matches_df]
            player_matches_df = pd.concat(frames)
        # save the result data frame
        player_matches_df.to_csv(f'../Data/PlayerMatches/DotaPlayer_{account_id}_Matches.csv', index=False)
