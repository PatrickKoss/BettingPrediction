import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BettingRestAPI.settings')
django.setup()

import pandas as pd
from datetime import datetime
from csgo_api.models import Player, Team


def migrate_players():
    player_df = pd.read_csv('./Data/Player.csv', index_col=False, header=0)
    cutting_date = datetime.now().replace(month=1, day=1, year=2019)
    player_df["Start_Date"] = pd.to_datetime(player_df["Start_Date"])
    player_df["End_Date"] = pd.to_datetime(player_df["End_Date"])
    player_df = player_df[player_df["Start_Date"] >= cutting_date]

    # replace the kast value in player df with a number
    player_df["Kast"] = player_df.Kast.str.replace(r'\%', '')
    player_df.replace(to_replace="-", value=0, inplace=True)
    player_df["Kast"] = player_df["Kast"].astype(float)
    player_df["Kast"] = 0.01 * player_df["Kast"]
    # drop rating column of a player
    player_df.drop(columns=["Rating"], inplace=True)

    for _, entry in player_df.iterrows():
        if not Player.objects.filter(name=entry["Name"], start_date=entry["Start_Date"],
                                     end_date=entry["End_Date"]).exists():
            model = Player.objects.create(name=entry["Name"], start_date=entry["Start_Date"],
                                          end_date=entry["End_Date"], dpr=entry["DPR"], kast=entry["Kast"],
                                          impact=entry["Impact"], adr=entry["ADR"], kpr=entry["KPR"])
            model.save()


def migrate_teams():
    team_df = pd.read_csv('./Data/Team.csv', index_col=False, header=0)
    team_df["Start_Date"] = pd.to_datetime(team_df["Start_Date"])
    team_df["End_Date"] = pd.to_datetime(team_df["End_Date"])
    team_df.drop(columns=["KD", "Wins", "Losses"], inplace=True)
    cutting_date = datetime.now().replace(month=1, day=1, year=2019)
    team_df = team_df[team_df["Start_Date"] >= cutting_date]
    for _, entry in team_df.iterrows():
        if not Team.objects.filter(name=entry["Name"], start_date=entry["Start_Date"],
                                   end_date=entry["End_Date"]).exists():
            if not Player.objects.filter(name=entry["Player_1"], start_date=entry["Start_Date"],
                                         end_date=entry["End_Date"]).exists():
                continue
            if not Player.objects.filter(name=entry["Player_2"], start_date=entry["Start_Date"],
                                         end_date=entry["End_Date"]).exists():
                continue
            if not Player.objects.filter(name=entry["Player_3"], start_date=entry["Start_Date"],
                                         end_date=entry["End_Date"]).exists():
                continue
            if not Player.objects.filter(name=entry["Player_4"], start_date=entry["Start_Date"],
                                         end_date=entry["End_Date"]).exists():
                continue
            if not Player.objects.filter(name=entry["Player_5"], start_date=entry["Start_Date"],
                                         end_date=entry["End_Date"]).exists():
                continue
            player_1 = Player.objects.filter(name=entry["Player_1"], start_date=entry["Start_Date"],
                                             end_date=entry["End_Date"]).first().id
            player_2 = Player.objects.filter(name=entry["Player_2"], start_date=entry["Start_Date"],
                                             end_date=entry["End_Date"]).first().id
            player_3 = Player.objects.filter(name=entry["Player_3"], start_date=entry["Start_Date"],
                                             end_date=entry["End_Date"]).first().id
            player_4 = Player.objects.filter(name=entry["Player_4"], start_date=entry["Start_Date"],
                                             end_date=entry["End_Date"]).first().id
            player_5 = Player.objects.filter(name=entry["Player_5"], start_date=entry["Start_Date"],
                                             end_date=entry["End_Date"]).first().id
            model = Team.objects.create(name=entry["Name"], start_date=entry["Start_Date"], end_date=entry["End_Date"],
                                        Player_1_id=player_1, Player_2_id=player_2, Player_3_id=player_3,
                                        Player_4_id=player_4,
                                        Player_5_id=player_5, winning_percentage=entry["Winning_Percentage"])
            model.save()


if __name__ == "__main__":
    migrate_teams()
