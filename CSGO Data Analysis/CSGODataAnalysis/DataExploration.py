import numpy as np
import pandas as pd


def save_complete_df(matches_df, team_df, player_df, filename):
    # create a complete team df which includes all player stats
    complete_team_df = get_complete_team_df(team_df, player_df)

    # create a copy of complete team df with renamed columns
    complete_team_df_team1 = get_renamed_team_df(complete_team_df, 1)

    # do the same copy for team 2
    complete_team_df_team2 = get_renamed_team_df(complete_team_df, 2)

    # create the complete data frame with all matches and their teams
    complete_df = matches_df.merge(complete_team_df_team1, left_on=['Team1'], right_on=['Team_1_Name'], how='inner')
    complete_df = get_filtered_complete_df_dates(complete_df, 1)

    complete_df = complete_df.merge(complete_team_df_team2, left_on=['Team2'], right_on=['Team_2_Name'], how='inner')
    complete_df = get_filtered_complete_df_dates(complete_df, 2)

    # drop unnecessary columns
    complete_df.drop(
        columns=["Date", "Team_1_Wins", "Team_1_Losses", "Team_2_Wins", "Team_2_Losses", "Team_1_KD",
                 "Team_2_KD"],
        inplace=True)
    for col in complete_df.columns:
        if "Name" in col:
            complete_df.drop(columns=[col], inplace=True)

    # drop '-' values
    for col in complete_df.columns:
        complete_df = complete_df[complete_df[col] != "-"]

    # add a win column. 0 Means team 1 won and 1 team 2.
    complete_df["Win"] = complete_df.apply(lambda row: 0 if row.Team1_Win == 1 else 1, axis=1)
    # drop now unnecessary team win columns
    complete_df.drop(columns=["Team1_Win", "Team2_Win"], inplace=True)

    # round values to 2
    complete_df = complete_df.round(2)
    # save complete df
    complete_df.to_csv(filename, index=False)


def get_dfs():
    """read in the csv files and convert the date columns to date time columns"""
    matches_df = pd.read_csv('./Data/Matches.csv', index_col=False, header=0)
    matches_df["Date"] = pd.to_datetime(matches_df["Date"])
    team_df = pd.read_csv('./Data/Team.csv', index_col=False, header=0)
    team_df["Start_Date"] = pd.to_datetime(team_df["Start_Date"])
    team_df["End_Date"] = pd.to_datetime(team_df["End_Date"])
    player_df = pd.read_csv('./Data/Player.csv', index_col=False, header=0)
    player_df["Start_Date"] = pd.to_datetime(player_df["Start_Date"])
    player_df["End_Date"] = pd.to_datetime(player_df["End_Date"])
    # drop unnecessary Map column
    matches_df.drop(columns=["Map"], inplace=True)
    # preprocess player data frame
    player_df = preprocess_player_df(player_df)
    return matches_df, team_df, player_df


def preprocess_player_df(player_df):
    """preprocess player df. Replace kast and drop rating"""
    # replace the kast value in player df with a number
    player_df["Kast"] = player_df.Kast.str.replace(r'\%', '')
    player_df.replace(to_replace="-", value=0, inplace=True)
    player_df["Kast"] = player_df["Kast"].astype(float)
    player_df["Kast"] = 0.01 * player_df["Kast"]

    # drop rating column of a player
    player_df.drop(columns=["Rating"], inplace=True)

    return player_df


def get_complete_team_df(team_df, player_df):
    """get a complete team data frame. It includes the team and all its players with their stats."""
    complete_team_df = team_df.copy()
    for i in range(5):
        player_df_copy = player_df.copy()
        columns_mapper = {}
        # get the rename dict for the columns
        for col in player_df_copy.columns:
            columns_mapper.update({col: "Player_{}_".format(i + 1) + col})
        # rename columns
        player_df_copy.rename(columns=columns_mapper, inplace=True)
        complete_team_df = complete_team_df.merge(player_df_copy,
                                                  left_on=['Player_{}'.format(i + 1), 'Start_Date', 'End_Date'],
                                                  right_on=['Player_{}_Name'.format(i + 1),
                                                            'Player_{}_Start_Date'.format(i + 1),
                                                            'Player_{}_End_Date'.format(i + 1)],
                                                  how='inner')
        # drop unnecessary columns
        complete_team_df.drop(columns=['Player_{}'.format(i + 1), 'Player_{}_Start_Date'.format(i + 1),
                                       'Player_{}_End_Date'.format(i + 1)], inplace=True)

    return complete_team_df


def get_renamed_team_df(complete_team_df, team_number):
    """get renamed complete team data frame. Every column starts after the transformation with Team_{team_number}_"""
    complete_team_df_team_x = complete_team_df.copy()
    columns_mapper_team = {}
    for col in complete_team_df_team_x.columns:
        columns_mapper_team.update({col: "Team_{}_".format(team_number) + col})
    complete_team_df_team_x.rename(columns=columns_mapper_team, inplace=True)

    return complete_team_df_team_x


def get_best_of_3_df():
    """This method returns a matches data frame that includes only best of 3 matches"""
    # get data frames
    matches_df, _, _ = get_dfs()

    # sort Team1 and Team2 according to their name
    matches_df["Team1"], matches_df["Team2"], matches_df["Team1_Win"], matches_df["Team2_Win"] = np.where(
        matches_df["Team1"] > matches_df["Team2"],
        [matches_df["Team2"], matches_df["Team1"], matches_df["Team2_Win"], matches_df["Team1_Win"]],
        [matches_df["Team1"], matches_df["Team2"], matches_df["Team1_Win"], matches_df["Team2_Win"]])

    # add a Rounds_Played column that includes how often two teams has played each other on a single day
    matches_df["Rounds_Played"] = matches_df.groupby(["Date", "Team1", "Team2"])["Team1"].transform("size")
    # filter out single matches
    matches_df = matches_df[matches_df["Rounds_Played"] > 1]
    # add a team1 win total column that will include the sum of all wins to get the total match result
    matches_df["Team1_Win_Total"] = matches_df.groupby(["Date", "Team1", "Team2"])["Team1_Win"].transform("sum")
    matches_df["Team2_Win_Total"] = matches_df.groupby(["Date", "Team1", "Team2"])["Team2_Win"].transform("sum")

    # drop team win columns
    matches_df.drop(columns=["Team1_Win", "Team2_Win"], inplace=True)
    # drop duplicates
    matches_df.drop_duplicates(inplace=True)

    matches_df.rename(columns={"Team1_Win_Total": "Team1_Win", "Team2_Win_Total": "Team2_Win"}, inplace=True)
    # filter out best of two matches
    matches_df = matches_df[((matches_df["Rounds_Played"] >= 2) & (matches_df["Team1_Win"] >= 2)) | (
      (matches_df["Rounds_Played"] >= 2) & (matches_df["Team2_Win"] >= 2))]

    # add final team win as 0 and 1
    matches_df["Team1_Win_Total"] = matches_df.apply(lambda row: 1 if row.Team1_Win >= 2 else 0, axis=1)
    matches_df["Team2_Win_Total"] = matches_df.apply(lambda row: 1 if row.Team2_Win >= 2 else 0, axis=1)

    # map rounds played to 0 and 1
    matches_df["Rounds_Played"] = matches_df.apply(lambda row: 0 if row.Rounds_Played == 2 else 1, axis=1)

    # reformat again
    matches_df.drop(columns=["Team1_Win", "Team2_Win"], inplace=True)
    matches_df.rename(columns={"Team1_Win_Total": "Team1_Win", "Team2_Win_Total": "Team2_Win"}, inplace=True)

    return matches_df


def get_filtered_complete_df_dates(complete_df, team_number):
    """returns the complete data frame filtered on Start_date <= Date <= End_date of joined complete data frame"""
    complete_df_res = complete_df[
        (complete_df[f"Team_{team_number}_Start_Date"] <= complete_df["Date"]) & (
          complete_df["Date"] <= complete_df[f"Team_{team_number}_End_Date"])]
    complete_df_res.drop(
        columns=[f"Team_{team_number}_Start_Date", f"Team_{team_number}_End_Date", f"Team{team_number}"], inplace=True)
    return complete_df_res


if __name__ == "__main__":
    matches_df, team_df, player_df = get_dfs()
    matches_df_best_of_3 = get_best_of_3_df()
    save_complete_df(matches_df, team_df, player_df, './Data/complete_matches.csv')
    # save_complete_df(matches_df_best_of_3, team_df, player_df, './Data/complete_matches_best_of_3.csv')
