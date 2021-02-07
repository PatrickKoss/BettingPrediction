import pandas as pd


def create_final_df():
    complete_df = pd.read_csv("./Data/completeMatches.csv", index_col=False, header=0)
    radiant_gold_per_minute = []
    radiant_xp_per_minute = []
    radiant_lane_efficient_points = []
    radiant_stuns_per_game = []
    radiant_tower_kills = []
    radiant_action_per_minute = []
    radiant_kd = []
    dire_gold_per_minute = []
    dire_xp_per_minute = []
    dire_lane_efficient_points = []
    dire_stuns_per_game = []
    dire_tower_kills = []
    dire_action_per_minute = []
    dire_kd = []
    for col in complete_df.columns:
        if col == "Radiant_Score":
            continue
        if col == "Dire_Score":
            continue
        if "Radiant_" in col and "Gold_Per_Minute" in col:
            radiant_gold_per_minute.append(col)
        if "Radiant_" in col and "XP_Per_Minute_" in col:
            radiant_xp_per_minute.append(col)
        if "Radiant_" in col and "Lane_Efficient_Points_Per_Game" in col:
            radiant_lane_efficient_points.append(col)
        if "Radiant_" in col and "Stuns_Per_Game" in col:
            radiant_stuns_per_game.append(col)
        if "Radiant_" in col and "Tower_Kills_Per_Game" in col:
            radiant_tower_kills.append(col)
        if "Radiant_" in col and "Actions_Per_Minute" in col:
            radiant_action_per_minute.append(col)
        if "Radiant_" in col and "_KD" in col:
            radiant_kd.append(col)
        if "Dire_" in col and "Gold_Per_Minute" in col:
            dire_gold_per_minute.append(col)
        if "Dire_" in col and "XP_Per_Minute_" in col:
            dire_xp_per_minute.append(col)
        if "Dire_" in col and "Lane_Efficient_Points_Per_Game" in col:
            dire_lane_efficient_points.append(col)
        if "Dire_" in col and "Stuns_Per_Game" in col:
            dire_stuns_per_game.append(col)
        if "Dire_" in col and "Tower_Kills_Per_Game" in col:
            dire_tower_kills.append(col)
        if "Dire_" in col and "Actions_Per_Minute" in col:
            dire_action_per_minute.append(col)
        if "Dire_" in col and "_KD" in col:
            dire_kd.append(col)
    complete_df_new = complete_df[["Radiant_Score", "Dire_Score", "Win"]].copy()
    complete_df_new["Radiant_Gold_Per_Minute_Per_Game"] = complete_df.loc[:, radiant_gold_per_minute].sum(axis=1)
    complete_df_new["Radiant_XP_Per_Minute_Per_Game"] = complete_df.loc[:, radiant_xp_per_minute].sum(axis=1)
    complete_df_new["Radiant_Lane_Efficient_Points_Per_Game"] = complete_df.loc[:, radiant_lane_efficient_points].sum(
        axis=1)
    complete_df_new["Radiant_Stuns_Per_Game"] = complete_df.loc[:, radiant_stuns_per_game].sum(axis=1)
    complete_df_new["Radiant_Tower_Kills_Per_Game"] = complete_df.loc[:, radiant_tower_kills].sum(axis=1)
    complete_df_new["Radiant_Actions_Per_Minute"] = complete_df.loc[:, radiant_action_per_minute].sum(axis=1)

    complete_df_new["Dire_Gold_Per_Minute_Per_Game"] = complete_df.loc[:, dire_gold_per_minute].sum(axis=1)
    complete_df_new["Dire_XP_Per_Minute_Per_Game"] = complete_df.loc[:, dire_xp_per_minute].sum(axis=1)
    complete_df_new["Dire_Lane_Efficient_Points_Per_Game"] = complete_df.loc[:, dire_lane_efficient_points].sum(
        axis=1)
    complete_df_new["Dire_Stuns_Per_Game"] = complete_df.loc[:, dire_stuns_per_game].sum(axis=1)
    complete_df_new["Dire_Tower_Kills_Per_Game"] = complete_df.loc[:, dire_tower_kills].sum(axis=1)
    complete_df_new["Dire_Actions_Per_Minute"] = complete_df.loc[:, dire_action_per_minute].sum(axis=1)

    print(complete_df.head().to_string())
    print(complete_df_new.head().to_string())
    complete_df_new.to_csv("./Data/completeMatchesNew.csv", index=False)


if __name__ == "__main__":
    create_final_df()
