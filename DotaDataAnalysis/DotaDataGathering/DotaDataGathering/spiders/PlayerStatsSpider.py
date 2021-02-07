import json
from datetime import datetime, timedelta

import pandas as pd
import scrapy


class PlayerStatsSpider(scrapy.Spider):
    # set the attributes for the spider
    name = "playerStats"

    def __init__(self, **kwargs):
        """initialize the data"""
        super().__init__(**kwargs)
        self.date_ranges = []
        start_date = datetime.strptime("2020-05-30", "%Y-%m-%d")
        # every player stat has a date range of 3 months. This list include a list of start and end dates every 3
        # months
        for x in range(0, 30 * 60, 90):
            end_date = start_date.replace(second=0, microsecond=0, hour=0, minute=0)
            start = end_date - timedelta(days=90)
            self.date_ranges.append({'start_date': start, 'end_date': end_date})
            start_date = start.replace(second=0)

        player_stats_df = pd.DataFrame(
            columns=['Account_ID', 'KD', 'Gold_Per_Minute_Per_Game', 'XP_Per_Minute_Per_Game',
                     'Lane_Efficient_Points_Per_Game',
                     'Hero_Damage_Per_Game', 'Tower_Damage_Per_Game', 'Hero_Healing_Per_Game', 'Stuns_Per_Game',
                     'Tower_Kills_Per_Game', 'Courier_Kills_Per_Game', 'Actions_Per_Minute_Per_Game', 'Start_Date',
                     'End_Date'])
        player_stats_sum_df = pd.DataFrame(
            columns=["Account_ID", "Kills_Sum", "Kills_Number", "Deaths_Sum", "Deaths_Number", "Gold_Per_Minute_Sum",
                     "Gold_Per_Minute_Number", "XP_Per_Minute_Sum", "XP_Per_Minute_Number", "Lane_Efficient_Points_Sum",
                     "Lane_Efficient_Points_Number", "Hero_Damage_Sum", "Hero_Damage_Number", "Tower_Damage_Sum",
                     "Tower_Damage_Number", "Hero_Healing_Sum", "Hero_Healing_Number", "Stuns_Sum", "Stuns_Number",
                     "Tower_Kills_Sum", "Tower_Kills_Number", "Courier_Kills_Sum", "Courier_Kills_Number",
                     "Actions_Per_Minute_Sum", "Actions_Per_Minute_Number", "Date", "Previous_Days"])
        player_stats_df.to_csv('../Data/DotaPlayerStats.csv', index=False)
        player_stats_sum_df.to_csv('../Data/DotaPlayerStatsSum.csv', index=False)

        # read in the dfs and convert the date column to a pandas datetime column
        self.player_stats_df = pd.read_csv('../Data/DotaPlayerStats.csv', index_col=False, header=0)
        self.player_stats_df["Start_Date"] = pd.to_datetime(self.player_stats_df["Start_Date"])
        self.player_stats_df["End_Date"] = pd.to_datetime(self.player_stats_df["End_Date"])
        self.player_df = pd.read_csv('../Data/DotaPlayer.csv', index_col=False, header=0)
        self.player_stats_sum = pd.read_csv('../Data/DotaPlayerStatsSum.csv', index_col=False, header=0)
        self.player_stats_sum["Date"] = pd.to_datetime(self.player_stats_sum["Date"])

    def start_requests(self):
        """start the data gathering"""
        urls = []
        for _, row in self.player_df.iterrows():
            for date_range in self.date_ranges:
                delta = self.date_ranges[0]["end_date"] - date_range["start_date"]
                urls.append(
                    {"url": f"https://api.opendota.com/api/players/{row['Account_ID']}/totals?date={delta.days}",
                     "date_range": date_range, "Account_ID": row["Account_ID"], "previous_days": delta.days})

        for url in urls:
            # check if entry already exist in the player stats data frame
            df = self.player_stats_df[(self.player_stats_df["Account_ID"] == url["Account_ID"]) & (
              self.player_stats_df["Start_Date"] == url["date_range"]["start_date"]) & (
                                        self.player_stats_df["End_Date"] == url["date_range"]["end_date"])]
            if len(df) > 0:
                continue

            yield scrapy.Request(url=url["url"], callback=self.parse,
                                 meta={"date_range": url["date_range"], "Account_ID": url["Account_ID"],
                                       "previous_days": url["previous_days"]})

    def parse(self, response):
        response_list = json.loads(response.text)
        date_range = response.meta.get('date_range')
        account_id = response.meta.get('Account_ID')
        previous_days = response.meta.get('previous_days')
        data_sum = {"Account_ID": account_id, "Date": date_range["start_date"], "Previous_Days": previous_days}
        data = {"Account_ID": account_id, "Start_Date": date_range["start_date"],
                "End_Date": date_range["end_date"]}

        # create the sum entry in the player stats sum data frame
        for res in response_list:
            if res["field"] == "kills":
                data_sum.update({"Kills_Sum": res["sum"], "Kills_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "deaths":
                data_sum.update({"Deaths_Sum": res["sum"] if res["sum"] > 0 else 1, "Deaths_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "gold_per_min":
                data_sum.update(
                    {"Gold_Per_Minute_Sum": res["sum"], "Gold_Per_Minute_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "xp_per_min":
                data_sum.update(
                    {"XP_Per_Minute_Sum": res["sum"], "XP_Per_Minute_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "lane_efficiency_pct":
                data_sum.update({"Lane_Efficient_Points_Sum": res["sum"],
                                 "Lane_Efficient_Points_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "hero_damage":
                data_sum.update({"Hero_Damage_Sum": res["sum"], "Hero_Damage_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "tower_damage":
                data_sum.update(
                    {"Tower_Damage_Sum": res["sum"], "Tower_Damage_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "hero_healing":
                data_sum.update(
                    {"Hero_Healing_Sum": res["sum"], "Hero_Healing_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "stuns":
                data_sum.update({"Stuns_Sum": res["sum"], "Stuns_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "tower_kills":
                data_sum.update({"Tower_Kills_Sum": res["sum"], "Tower_Kills_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "courier_kills":
                data_sum.update(
                    {"Courier_Kills_Sum": res["sum"], "Courier_Kills_Number": res["n"] if res["n"] > 0 else 1})
            if res["field"] == "actions_per_min":
                data_sum.update({"Actions_Per_Minute_Sum": res["sum"],
                                 "Actions_Per_Minute_Number": res["n"] if res["n"] > 0 else 1})

        # merge the result data frame with the current data frame
        data_df = pd.DataFrame(data_sum, index=[len(self.player_stats_sum)])
        frames = [data_df, self.player_stats_sum]
        self.player_stats_sum = pd.concat(frames)
        # save the sum data frame
        self.player_stats_sum.to_csv('../Data/DotaPlayerStatsSum.csv', index=False)

        # create the player stats entry for the result data frame
        if previous_days == 90:
            data.update({"KD": data_sum["Kills_Sum"] / data_sum["Deaths_Sum"],
                         "Gold_Per_Minute_Per_Game": data_sum["Gold_Per_Minute_Sum"] / data_sum[
                             "Gold_Per_Minute_Number"],
                         "XP_Per_Minute_Per_Game": data_sum["XP_Per_Minute_Sum"] / data_sum[
                             "XP_Per_Minute_Number"],
                         "Lane_Efficient_Points_Per_Game": data_sum["Lane_Efficient_Points_Sum"] / data_sum[
                             "Lane_Efficient_Points_Number"],
                         "Hero_Damage_Per_Game": data_sum["Hero_Damage_Sum"] / data_sum[
                             "Hero_Damage_Number"], "Tower_Damage_Per_Game": data_sum["Tower_Damage_Sum"] / data_sum[
                    "Tower_Damage_Number"], "Hero_Healing_Per_Game": data_sum["Hero_Healing_Sum"] / data_sum[
                    "Hero_Healing_Number"], "Stuns_Per_Game": data_sum["Stuns_Sum"] / data_sum[
                    "Stuns_Number"], "Tower_Kills_Per_Game": data_sum["Tower_Kills_Sum"] / data_sum[
                    "Tower_Kills_Number"], "Courier_Kills_Per_Game": data_sum["Courier_Kills_Sum"] / data_sum[
                    "Courier_Kills_Number"],
                         "Actions_Per_Minute_Per_Game": data_sum["Actions_Per_Minute_Sum"] / data_sum[
                             "Actions_Per_Minute_Number"]})
        else:
            previous_df = self.player_stats_sum[(self.player_stats_sum["Account_ID"] == account_id) & (
              self.player_stats_sum["Date"] == date_range["end_date"])]
            kills = 0
            deaths = 0
            for res in response_list:
                if res["field"] == "kills":
                    kills = res["sum"] - previous_df["Kills_Sum"].values[0]
                if res["field"] == "deaths":
                    deaths = res["sum"] - previous_df["Deaths_Sum"].values[0]
                if res["field"] == "gold_per_min":
                    up = res["sum"] - previous_df["Gold_Per_Minute_Sum"].values[0]
                    denominator = res["n"] - previous_df["Gold_Per_Minute_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Gold_Per_Minute_Per_Game": up / denominator})
                if res["field"] == "xp_per_min":
                    up = res["sum"] - previous_df["XP_Per_Minute_Sum"].values[0]
                    denominator = res["n"] - previous_df["XP_Per_Minute_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"XP_Per_Minute_Per_Game": up / denominator})
                if res["field"] == "lane_efficiency_pct":
                    up = res["sum"] - previous_df["Lane_Efficient_Points_Sum"].values[0]
                    denominator = res["n"] - previous_df["Lane_Efficient_Points_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Lane_Efficient_Points_Per_Game": up / denominator})
                if res["field"] == "hero_damage":
                    up = res["sum"] - previous_df["Hero_Damage_Sum"].values[0]
                    denominator = res["n"] - previous_df["Hero_Damage_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Hero_Damage_Per_Game": up / denominator})
                if res["field"] == "tower_damage":
                    up = res["sum"] - previous_df["Tower_Damage_Sum"].values[0]
                    denominator = res["n"] - previous_df["Tower_Damage_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Tower_Damage_Per_Game": up / denominator})
                if res["field"] == "hero_healing":
                    up = res["sum"] - previous_df["Hero_Healing_Sum"].values[0]
                    denominator = res["n"] - previous_df["Hero_Healing_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Hero_Healing_Per_Game": up / denominator})
                if res["field"] == "stuns":
                    up = res["sum"] - previous_df["Stuns_Sum"].values[0]
                    denominator = res["n"] - previous_df["Stuns_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Stuns_Per_Game": up / denominator})
                if res["field"] == "tower_kills":
                    up = res["sum"] - previous_df["Tower_Kills_Sum"].values[0]
                    denominator = res["n"] - previous_df["Tower_Kills_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Tower_Kills_Per_Game": up / denominator})
                if res["field"] == "courier_kills":
                    up = res["sum"] - previous_df["Courier_Kills_Sum"].values[0]
                    denominator = res["n"] - previous_df["Courier_Kills_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Courier_Kills_Per_Game": up / denominator})
                if res["field"] == "actions_per_min":
                    up = res["sum"] - previous_df["Actions_Per_Minute_Sum"].values[0]
                    denominator = res["n"] - previous_df["Actions_Per_Minute_Number"].values[0]
                    denominator = denominator if denominator > 0 else 1
                    data.update({"Actions_Per_Minute": up / denominator})
            data.update({"KD": kills / (deaths if deaths > 0 else 1)})
        # merge the result data frame with the current data frame
        data_df = pd.DataFrame(data, index=[len(self.player_stats_df)])
        frames = [data_df, self.player_stats_df]
        self.player_stats_df = pd.concat(frames)
        # save the result data frame
        self.player_stats_df.to_csv('../Data/DotaPlayerStats.csv', index=False)
