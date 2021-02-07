import random

import numpy as np
import pandas as pd


def create_final_df():
    match_df, team_df = get_pro_match_df()
    player_stats_df = get_prepared_player_stats_df()
    # radiant_df, dire_df = get_radiant_dire_df_with_account_columns(match_df, team_df)
    match_df = prepare_match_df(match_df)
    match_df.drop(columns=["Radiant_Team_ID", "Dire_Team_ID"], inplace=True)
    match_df = get_match_df_with_team_accounts(match_df)
    # join player stats and accounts in matches together
    match_df = get_merges_matches_player_stats_df(match_df, "Radiant", player_stats_df)
    match_df = get_merges_matches_player_stats_df(match_df, "Dire", player_stats_df)
    # drop last unnecessary column and round values
    match_df.drop(columns=["Start_Time"], inplace=True)
    match_df = match_df.round(2)
    match_df.to_csv("./Data/completeMatches.csv", index=False)


def get_merges_matches_player_stats_df(matches_df, team_cat, player_stats_df):
    match_df = matches_df.copy()
    for i in range(5):
        radiant_player_stats = player_stats_df.copy()
        for col in radiant_player_stats.columns:
            radiant_player_stats.rename(columns={col: f"{team_cat}_{i}_{col}"}, inplace=True)
        match_df = match_df.merge(radiant_player_stats, left_on=f"{team_cat}_Account_ID_{i}",
                                  right_on=f"{team_cat}_{i}_Account_ID", how="inner")
        match_df = match_df[(match_df[f"{team_cat}_{i}_Start_Date"] < match_df["Start_Time"]) & (
          match_df["Start_Time"] <= match_df[f"{team_cat}_{i}_End_Date"])]
        match_df.drop(columns=[f"{team_cat}_{i}_Start_Date", f"{team_cat}_{i}_End_Date", f"{team_cat}_Account_ID_{i}",
                               f"{team_cat}_{i}_Account_ID"], inplace=True)
    return match_df


def get_prepared_player_stats_df():
    player_stats_df = pd.read_csv("../DotaDataGathering/Data/DotaPlayerStats.csv", index_col=False, header=0)
    player_stats_df.drop(columns=["Hero_Healing_Per_Game", "Actions_Per_Minute_Per_Game",
                                  "Tower_Damage_Per_Game", "Hero_Damage_Per_Game"],
                         inplace=True)
    player_stats_df.rename(columns={"Actions_Per_Minute": "Actions_Per_Minute_Per_Game"})
    player_stats_df["Start_Date"] = pd.to_datetime(player_stats_df["Start_Date"])
    player_stats_df["End_Date"] = pd.to_datetime(player_stats_df["End_Date"])
    return player_stats_df


def get_match_df_with_team_accounts(matches_df):
    match_df = matches_df.copy()
    radiant_df = pd.read_csv("./Data/RadiantAccountMatches.csv", index_col=False, header=0)
    dire_df = pd.read_csv("./Data/DireAccountMatches.csv", index_col=False, header=0)
    radiant_df.drop(columns=["Team_ID"], inplace=True)
    dire_df.drop(columns=["Team_ID"], inplace=True)

    # merge radiant team
    match_df = match_df.merge(radiant_df, left_on=["Match_ID"], right_on=["Match_ID"], how="inner")
    # rearrange radiant columns
    for i in range(0, 5, 1):
        column = match_df[f"Radiant_Account_ID_{i}"]
        match_df.drop(columns=[f"Radiant_Account_ID_{i}"], inplace=True)
        match_df.insert(i + 1, f"Radiant_Account_ID_{i}", column)

    # merge dire team
    match_df = match_df.merge(dire_df, left_on=["Match_ID"], right_on=["Match_ID"], how="inner")
    # rearrange dire columns
    for i in range(0, 5, 1):
        column = match_df[f"Dire_Account_ID_{i}"]
        match_df.drop(columns=[f"Dire_Account_ID_{i}"], inplace=True)
        match_df.insert(i + 6, f"Dire_Account_ID_{i}", column)
    match_df.drop(columns=["Match_ID"], inplace=True)
    return match_df


def get_pro_match_df():
    team_df = pd.read_csv("../DotaDataGathering/Data/DotaTeamPlayers.csv", index_col=False, header=0)
    player_df = pd.read_csv("../DotaDataGathering/Data/DotaPlayer.csv", index_col=False, header=0)
    matches_df = pd.read_csv("../DotaDataGathering/Data/DotaMatches.csv", index_col=False, header=0)
    matches_df.dropna(inplace=True)
    matches_df["Start_Time"] = pd.to_datetime(matches_df["Start_Time"])
    matches_df["Win"] = matches_df.apply(lambda row: 0 if row.Radiant_Win == 1 else 1, axis=1)
    matches_df.drop(columns=["Radiant_Win", "Dire_Win"], inplace=True)
    # print('matches length: ', len(matches_df))
    # print('unique accounts in teams df: ', len(team_df["Account_ID"].unique()))
    team_df.drop(columns=["Is_Current_Member"], inplace=True)
    # team_df = team_df[team_df["Games_Played"] >= 10]

    # get the pros id to filter out matches where only pros played
    pros_id = player_df[["Account_ID"]].copy()
    pros_id.rename(columns={"Account_ID": "Pros_ID"}, inplace=True)
    team_df = team_df.merge(pros_id, left_on="Account_ID", right_on="Pros_ID", how="inner")
    team_df["Number_Of_Players"] = team_df.groupby(["Team_ID"])["Team_ID"].transform("size")
    # we only want teams with more than 5 players to later fill the match with 5 players
    team_df = team_df[team_df["Number_Of_Players"] >= 5]
    # print("unique accounts in teams df after transformation: ", len(team_df["Account_ID"].unique()))

    # start filtering the matches according to the modified teams df
    team_names_games = team_df[["Team_ID", "Number_Of_Players"]].copy()
    team_names_games.drop_duplicates(inplace=True)
    radiant_team_names_games = team_names_games.copy()
    dire_team_names_games = team_names_games.copy()
    for col in radiant_team_names_games:
        radiant_team_names_games.rename(columns={col: "Radiant_" + col}, inplace=True)
    for col in dire_team_names_games:
        dire_team_names_games.rename(columns={col: "Dire_" + col}, inplace=True)
    matches_df = matches_df.merge(radiant_team_names_games, how="inner", left_on="Radiant_Team_ID",
                                  right_on="Radiant_Team_ID")
    matches_df = matches_df.merge(dire_team_names_games, how="inner", left_on="Dire_Team_ID",
                                  right_on="Dire_Team_ID")
    matches_df.drop(columns=["Radiant_Number_Of_Players", "Dire_Number_Of_Players"], inplace=True)
    team_df.drop(columns=["Pros_ID"], inplace=True)
    # print("Pros only matches length: ", len(matches_df))
    # print(matches_df.head(20).to_string())
    # print(team_df.head(20).to_string())
    return matches_df, team_df


def get_radiant_dire_df_with_account_columns(matches_df, team_df):
    match_df = prepare_match_df(matches_df)
    radiant_df = get_match_account_df("Radiant")
    dire_df = get_match_account_df("Dire")
    for index, row in match_df.iterrows():
        team_accounts_radiant = team_df[team_df["Team_ID"] == row["Radiant_Team_ID"]]
        team_accounts_dire = team_df[team_df["Team_ID"] == row["Dire_Team_ID"]]
        radiant_data_df = get_team_account_df(team_accounts_radiant, row["Match_ID"], row["Radiant_Team_ID"], "Radiant",
                                              radiant_df)
        dire_data_df = get_team_account_df(team_accounts_dire, row["Match_ID"], row["Dire_Team_ID"], "Dire",
                                           dire_df)
        radiant_df = pd.concat([radiant_data_df, radiant_df])
        dire_df = pd.concat([dire_data_df, dire_df])
        if index % 500 == 0:
            radiant_df.to_csv('./Data/RadiantAccountMatches.csv', index=False)
            dire_df.to_csv('./Data/DireAccountMatches.csv', index=False)
    radiant_df.to_csv('./Data/RadiantAccountMatches.csv', index=False)
    dire_df.to_csv('./Data/DireAccountMatches.csv', index=False)
    return radiant_df, dire_df


def get_team_account_df(team_accounts, match_ID, team_ID, team_name_cat, res_df):
    team_accounts_list = np.array(team_accounts["Account_ID"])
    accounts = []
    for account_ID in team_accounts_list:
        team_account_df = pd.read_csv(
            f"../DotaDataGathering/Data/PlayerMatches/DotaPlayer_{account_ID}_Matches.csv", index_col=False,
            header=0)
        if len(team_account_df[team_account_df["Match_ID"] == match_ID]) == 1:
            accounts.append(account_ID)
        if len(accounts) == 5:
            break
    # for some reason accounts can be less than 5 accounts which probably mean that we dont have all matches
    # for each player in the team. So we randomize missing accounts from the team players
    if len(accounts) <= 4:
        # remove accounts from team_account_list
        team_accounts_list = np.setdiff1d(team_accounts_list, np.array(accounts))
        # append random choice from remaining team_account_list
        for _ in range(len(accounts), 5, 1):
            accounts.append(np.random.choice(team_accounts_list, 1)[0])
    # shuffle accounts
    random.shuffle(accounts)
    # add accounts to the result data frame
    data = {"Match_ID": match_ID, "Team_ID": team_ID}
    for i, account in enumerate(accounts):
        data.update({f"{team_name_cat}_Account_ID_{i}": account})
    data_df = pd.DataFrame(data, index=[len(res_df)])
    return data_df


def get_match_account_df(team_cat):
    columns = ["Match_ID", "Team_ID"]
    for i in range(5):
        columns.append(f"{team_cat}_Account_ID_{i}")
    return pd.DataFrame(columns=columns)


def drop_insert_column_df_at_index(df, col, index):
    column = df[col]
    df.drop(columns=[col], inplace=True)
    df.insert(index, col, column)


def prepare_match_df(matches_df):
    match_df = matches_df.copy()
    # drop unnecessary columns
    match_df.drop(columns=["Radiant_Name", "Dire_Name", "League_Name", "League_ID"], inplace=True)
    drop_insert_column_df_at_index(match_df, "Duration", len(match_df.columns) - 1)
    drop_insert_column_df_at_index(match_df, "Start_Time", len(match_df.columns) - 1)
    return match_df


if __name__ == "__main__":
    create_final_df()
