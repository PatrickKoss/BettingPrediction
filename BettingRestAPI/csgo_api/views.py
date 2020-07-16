import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from BettingRestAPI.Helper.CSGOHelper import check_authorization
from BettingRestAPI.Serializer.CSGOSerializer import MatchSerializer, TeamSerializer, TeamsPredictionSerializer
from BettingRestAPI.Serializer.Encoder import ComplexEncoder
from BettingRestAPI.utils.Message import Message
from csgo_api.models import MatchResult, Match, Team


class GetUpcomingMatches(APIView):
    def get(self, request):
        """return all upcoming matches. Matches need to start later than now"""
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Upcoming Matches")
            upcoming_matches = Match.objects.filter(
                date__range=(datetime.now(), datetime.now() + timedelta(days=15))).order_by("date")
            upcoming_matches = MatchSerializer(upcoming_matches, context={'request': request}, many=True).data
            for match in upcoming_matches:
                match.update({
                    "nnPickedTeam": match["Team_1"]["name"] if match["team_1_confidence"] >= match["team_2_confidence"]
                    else match["Team_2"]["name"]})
                match.update({
                    "svmPickedTeam": match["Team_1"]["name"] if float(match["prediction_svm"]) == 0 else match["Team_2"][
                        "name"]})
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetMatchResult(APIView):
    def get(self, request):
        """return the result of the matches"""
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            matches_result = MatchResult.objects.all().order_by("-date")
            # if there are no matches in the database then return an empty array
            if len(matches_result) == 0:
                json_rep = json.dumps({'message': message.repr_json(), 'matchResult': []},
                                      cls=ComplexEncoder)
                json_rep = json.loads(json_rep)
                return Response(json_rep, status=response_status)
            upcoming_matches = Match.objects.all().order_by("-date")
            # create pandas data frame to merge upcoming matches and result matches on certain attributes
            df_matches_result = pd.DataFrame(list(matches_result.values()))
            df_upcoming_matches = pd.DataFrame(list(upcoming_matches.values()))
            df_upcoming_matches.drop(columns=["id"], inplace=True)
            df_matches_result.drop(columns=["id"], inplace=True)
            df_result = df_matches_result.merge(df_upcoming_matches, left_on=["Team_1_id", "Team_2_id", "date"],
                                                right_on=["Team_1_id", "Team_2_id", "date"], how="inner")
            # convert strings to float type
            df_result["team_1_win"] = df_result["team_1_win"].astype(float)
            df_result["team_2_win"] = df_result["team_2_win"].astype(float)
            df_result["odds_team_1"] = df_result["odds_team_1"].astype(float)
            df_result["odds_team_2"] = df_result["odds_team_2"].astype(float)
            df_result["team_1_confidence"] = df_result["team_1_confidence"].astype(float)
            df_result["team_2_confidence"] = df_result["team_2_confidence"].astype(float)
            df_result["prediction_svm"] = df_result["prediction_svm"].astype(float)
            # convert data frame to dict
            result = df_result.to_dict('records')
            # modify dict for correct values
            for d in result:
                match = upcoming_matches.filter(date=d["date"], Team_1_id=d["Team_1_id"],
                                                Team_2_id=d["Team_2_id"]).first()
                team_1_name = match.Team_1.name
                team_2_name = match.Team_2.name
                winning_team = team_1_name if d["team_1_win"] else team_2_name
                nn_picked_team = team_1_name if d["team_1_confidence"] >= d[
                    "team_2_confidence"] else team_2_name
                svm_picked_team = team_1_name if float(d["prediction_svm"]) == 0 else team_2_name
                d.update({"Team1": team_1_name, "Team2": team_2_name, "date": d["date"].isoformat(),
                          "nnPickedTeam": nn_picked_team, "svmPickedTeam": svm_picked_team,
                          "winningTeam": winning_team})
            json_rep = json.dumps({'message': message.repr_json(), 'matchResult': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetMatchResultStats(APIView):
    def get(self, request):
        """return json of stats that the model produces"""
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            matches_result = MatchResult.objects.all()
            upcoming_matches = Match.objects.all()
            # create pandas data frame for faster computation
            df_matches_result = pd.DataFrame(list(matches_result.values()))
            df_upcoming_matches = pd.DataFrame(list(upcoming_matches.values()))
            df_upcoming_matches.drop(columns=["id"], inplace=True)
            df_matches_result.drop(columns=["id"], inplace=True)
            df_result = df_matches_result.merge(df_upcoming_matches, left_on=["Team_1_id", "Team_2_id", "date"],
                                                right_on=["Team_1_id", "Team_2_id", "date"], how="inner")
            df_result["prediction_svm"] = df_result["prediction_svm"].astype(float)
            # df_result = df_result[(df_result["odds_team_1"] <= 4.5) & (df_result["odds_team_2"] <= 4.5)]
            # create the result dicts
            result = []
            self.create_result_list(df_result, result, False)
            self.create_result_list(df_result, result, False, mode="BO1")
            self.create_result_list(df_result, result, False, mode="BO3")
            self.create_result_list(df_result, result, True)
            self.create_result_list(df_result, result, True, mode="BO1")
            self.create_result_list(df_result, result, True, mode="BO3")
            self.create_result_list(df_result, result, True, nn=True)
            self.create_result_list(df_result, result, True, mode="BO1", nn=True)
            self.create_result_list(df_result, result, True, mode="BO3", nn=True)

            result = sorted(result, key=lambda k: k["odds"], reverse=False)

            json_rep = json.dumps({'message': message.repr_json(),
                                   'stats': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)

    def get_df_with_threshold(self, df, threshold):
        """method returns a data frame with confidence over a certain threshold"""
        return df[((df["odds_team_1"] > threshold) & (df["team_1_confidence"] >= df["team_2_confidence"])) | (
          (df["odds_team_2"] > threshold) & (df["team_2_confidence"] >
                                             df["team_1_confidence"]))]

    def get_df_with_threshold_svm(self, df, threshold):
        """method returns a data frame with confidence over a certain threshold"""
        return df[((df["odds_team_1"] > threshold) & (df["prediction_svm"] == 0)) | (
          (df["odds_team_2"] > threshold) & (df["prediction_svm"] == 1))]

    def get_df_with_money(self, df):
        """method returns a data frame exact as the given data frame but with a money column. This columns returns the
        money of a bet. If the model was correct then the return is the odds - 1 else it is -1"""
        copy_df = df.copy()
        copy_df["money"] = df.apply(
            lambda row: (float(row.odds_team_1) - 1) if row.team_1_win == 1
                                                        and row.team_1_confidence >= row.team_2_confidence
            else (float(
                row.odds_team_2) - 1) if row.team_2_win == 1 and row.team_1_confidence < row.team_2_confidence else -1,
            axis=1)
        return copy_df

    def get_df_with_money_svm(self, df):
        """return a data frame with the money made on a bet"""
        copy_df = df.copy()
        copy_df["money"] = df.apply(
            lambda row: (float(row.odds_team_1) - 1) if row.team_1_win == 1
                                                        and row.prediction_svm == 0
            else (float(
                row.odds_team_2) - 1) if row.team_2_win == 1 and row.prediction_svm == 1 else -1,
            axis=1)
        return copy_df

    def get_filtered_df_nn_svm(self, df):
        """return a data frame with the money made on a bet"""
        copy_df = df.copy()
        copy_df = copy_df[
            (copy_df["team_1_confidence"] > copy_df["team_2_confidence"]) & (copy_df["prediction_svm"] == 0) | (
                  copy_df["team_2_confidence"] > copy_df["team_1_confidence"]) & (copy_df["prediction_svm"] == 1)]
        return copy_df

    def get_roi(self, df):
        """return the total roi of the model"""
        return round(float((df["money"].sum()) / len(df)), 2)

    def get_accuracy(self, df):
        """return the total accuracy. Every money entry that made money"""
        return round(float(len(df[df["money"] >= 0]) / len(df)), 2)

    def get_df_odds_threshold(self, df, odds):
        """return a data frame with a given odds threshold"""
        return df[(df["odds_team_1"] >= odds) & (df["odds_team_2"] >= odds)]

    def get_average_odds(self, df):
        """This method calculates the average odds of all bets"""
        filter_team_1_df = df[df["team_1_win"] == 1]
        result_array = np.array([filter_team_1_df["odds_team_1"]])
        filter_team_2_df = df[df["team_2_win"] == 1]
        result_array = np.concatenate((result_array, np.array([filter_team_2_df["odds_team_2"]])), axis=1)
        average_odds = sum(result_array[0]) / len(result_array[0] if len(result_array[0]) > 0 else 1)
        average_odds = round(float(average_odds), 2)
        return average_odds

    def get_average_winning_odds(self, df):
        """return the average winning odds of the model."""
        filtered_df = df[df["money"] > 0]
        winnings_array = np.array(filtered_df["money"])
        average_winning_odds = sum(winnings_array) / len(winnings_array) if len(winnings_array) > 0 else 1
        return round(float(average_winning_odds) + 1, 2)

    def create_result_list(self, df_result, result, svm, nn=False, mode=None):
        """method returns a result list of dicts"""
        df_copy = df_result.copy()
        if mode is not None:
            df_copy = df_result[df_result["mode"] == mode]
        for odd in np.arange(1, 1.9, 0.1):
            odd = round(odd, 2)
            if not svm and not nn:
                df = self.get_df_with_threshold(df_copy, odd)
            elif not nn:
                df = self.get_df_with_threshold_svm(df_copy, odd)
            else:
                df = self.get_df_with_threshold(df_copy, odd)
                df = self.get_df_with_threshold_svm(df, odd)
            if len(df) == 0:
                continue
            if svm and not nn:
                df = self.get_df_with_money_svm(df)
            elif not nn:
                df = self.get_df_with_money(df)
            else:
                df = self.get_filtered_df_nn_svm(df)
                df = self.get_df_with_money(df)
            if len(df) == 0:
                continue
            # if len(df) < len(df_result) * 0.2:
            #     continue
            roi = self.get_roi(df)
            average_odds = self.get_average_odds(df)
            average_winning_odds = self.get_average_winning_odds(df)
            if mode is None:
                mode_selected = "all games"
            else:
                mode_selected = mode
            if svm and not nn:
                model = "SVM"
            elif not nn:
                model = "NN"
            else:
                model = "NSM"
            result.append(
                {"accuracy": self.get_accuracy(df),
                 "roi": roi, "sampleSize": len(df), "averageOdds": average_odds, "svm": model,
                 "mode": mode_selected,
                 "odds": odd, "average_winning_odds": average_winning_odds})


class GetTeam(APIView):
    def get(self, request, id):
        """return the team given by an id"""
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"Here is the Team")
            team = Team.objects.filter(id=id)
            if not team.exists():
                message = Message("error", f"No team found")
                json_rep = json.dumps({'message': message.repr_json()},
                                      cls=ComplexEncoder)
                return Response(json_rep, status=response_status)
            team = team.first()
            team = TeamSerializer(team, context={'request': request}).data
            json_rep = json.dumps({'message': message.repr_json(), 'team': team},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetTeams(APIView):
    def get(self, request):
        """return all teams"""
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"Here are the teams")
            teams = Team.objects.all().order_by("end_date")
            team_set = list({team.name: team for team in teams}.values())
            team_set.sort(key=lambda x: x.name)
            teams = TeamsPredictionSerializer(team_set, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'teams': teams},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class CreatePrediction(APIView):
    def post(self, request):
        """make a prediction on two given teams"""
        check, json_message, response_status = check_authorization(request)
        if check:
            data = json.loads(request.body or "{}")
            # check if the teams are correct
            check_teams, response = self.check_teams(data)
            if not check_teams:
                return response
            # check if the players are correct
            check_player_team_1, response = self.check_players_in_team(data, "team_1")
            if not check_player_team_1:
                return response
            check_player_team_2, response = self.check_players_in_team(data, "team_1")
            if not check_player_team_2:
                return response
            # check if a single player is correct
            check_players, response = self.check_players(data)
            if not check_players:
                return response
            # check if the values are correct
            validate_data, response = self.validate_data(data)
            if not validate_data:
                return response

            message = Message("success", f"Prediction")
            # create a prediction array and make a prediction
            prediction_array = np.array([[data["team_1"]["winning_percentage"]]])
            prediction_array = np.concatenate((prediction_array,
                                               self.get_team_player_array(data["team_1"]["Player_1"],
                                                                          data["team_1"]["Player_2"],
                                                                          data["team_1"]["Player_3"],
                                                                          data["team_1"]["Player_4"],
                                                                          data["team_1"]["Player_5"])), axis=1)
            prediction_array = np.concatenate((prediction_array, np.array([[data["team_2"]["winning_percentage"]]])),
                                              axis=1)
            prediction_array = np.concatenate((prediction_array,
                                               self.get_team_player_array(data["team_2"]["Player_1"],
                                                                          data["team_2"]["Player_2"],
                                                                          data["team_2"]["Player_3"],
                                                                          data["team_2"]["Player_4"],
                                                                          data["team_2"]["Player_5"])), axis=1)
            # if data["mode"] == "BO1":
            #     prediction_model = settings.PREDICTION_MODEL_ALL_WINS
            #     prediction_model_svm = settings.PREDICTION_MODEL_SVM_ALL_WINS
            # else:
            #     prediction_model = settings.PREDICTION_MODEL_BO3_WINS
            #     prediction_model_svm = settings.PREDICTION_MODEL_SVM_BO3_WINS
            # get the right model
            prediction_model = settings.PREDICTION_MODEL_ALL_WINS
            prediction_model_svm = settings.PREDICTION_MODEL_SVM_ALL_WINS

            prediction_svm = prediction_model_svm.predict(prediction_array)
            team_2_confidence = round(prediction_model.predict(prediction_array)[0][0], 4)
            team_1_confidence = round(1 - team_2_confidence, 4)
            team_1_confidence = team_1_confidence.item()
            team_2_confidence = team_2_confidence.item()
            team_2_confidence = round(team_2_confidence, 4)
            team_1_confidence = round(team_1_confidence, 4)
            json_rep = json.dumps({'message': message.repr_json(),
                                   'prediction': {"team_1_confidence": team_1_confidence,
                                                  "team_2_confidence": team_2_confidence,
                                                  "prediction_svm": prediction_svm[0]}},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)

    def get_player_stats_array(self, player):
        """returns a numpy array of player stats"""
        return np.array([[player["dpr"], player["kast"], player["impact"], player["adr"], player["kpr"]]])

    def get_team_player_array(self, player1, player2, player3, player4, player5):
        """return a numpy array of team stats"""
        team_player_array = self.get_player_stats_array(player1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player2)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player3)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player4)), axis=1)
        return np.concatenate((team_player_array, self.get_player_stats_array(player5)), axis=1)

    def check_teams(self, data):
        """checks if a team is in the data sent"""
        if "team_1" not in data or "team_2" not in data:
            message = Message("error", f"No teams sent")
            json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
        else:
            return True, ""

    def check_players_in_team(self, data, team):
        """checks if players are sent in the data"""
        if "Player_1" not in data[team] or "Player_2" not in data[team] or "Player_3" not in data[
            team] or "Player_4" not in data[team] or "Player_5" not in data[team]:
            message = Message(f"error", f"No player for {team} sent")
            json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
        else:
            return True, ""

    def check_players(self, data):
        """checks if the players has the right attributes in the data sent"""
        team_list = ["team_1", "team_2"]
        player_list = ["Player_1", "Player_2", "Player_3", "Player_4", "Player_5"]
        for team in team_list:
            for player in player_list:
                if "adr" not in data[team][player] or "dpr" not in data[team][player] or "kast" not in data[team][
                    player] or "impact" not in data[team][player] or "kpr" not in data[team][player]:
                    message = Message(f"error", f"No stats sent for {player} in {team}")
                    json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
                    json_rep = json.loads(json_rep)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return True, ""

    def validate_data(self, data):
        """check if the data attributes are in the correct value range"""
        team_list = ["team_1", "team_2"]
        player_list = ["Player_1", "Player_2", "Player_3", "Player_4", "Player_5"]
        for team in team_list:
            try:
                float(data[team]["winning_percentage"])
            except:
                message = Message(f"error", f"Winning percentage of {team} is not of type float")
                json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
                json_rep = json.loads(json_rep)
                return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
            if 0 <= float(data[team]["winning_percentage"]) <= 1:
                pass
            else:
                message = Message(f"error", f"Winning percentage of {team} is not between 0 and 1")
                json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
                json_rep = json.loads(json_rep)
                return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
            for player in player_list:
                try:
                    float(data[team][player]["adr"])
                except:
                    json_rep = self.get_error_message_player_stat("adr", player)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                try:
                    float(data[team][player]["dpr"])
                except:
                    json_rep = self.get_error_message_player_stat("dpr", player)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                try:
                    float(data[team][player]["kast"])
                except:
                    json_rep = self.get_error_message_player_stat("kast", player)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                try:
                    float(data[team][player]["impact"])
                except:
                    json_rep = self.get_error_message_player_stat("impact", player)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                try:
                    float(data[team][player]["kpr"])
                except:
                    json_rep = self.get_error_message_player_stat("kpr", player)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                if 0 <= float(data[team][player]["adr"]) <= 1000:
                    pass
                else:
                    json_rep = self.get_error_message_player_stat_in_range("adr", player, 0, 1000)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                if 0 <= float(data[team][player]["dpr"]) <= 1:
                    pass
                else:
                    json_rep = self.get_error_message_player_stat_in_range("dpr", player, 0, 1)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                if 0 <= float(data[team][player]["kast"]) <= 10:
                    pass
                else:
                    json_rep = self.get_error_message_player_stat_in_range("kast", player, 0, 10)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                if 0 <= float(data[team][player]["impact"]) <= 5:
                    pass
                else:
                    json_rep = self.get_error_message_player_stat_in_range("impact", player, 0, 5)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
                if 0 <= float(data[team][player]["kpr"]) <= 10:
                    pass
                else:
                    json_rep = self.get_error_message_player_stat_in_range("kpr", player, 0, 10)
                    return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
        return True, ""

    def get_error_message_player_stat(self, stat, player):
        """get a error message when the attribute is not a correct type"""
        message = Message(f"error", f"{stat} of {player} is not of type float")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return json_rep

    def get_error_message_player_stat_in_range(self, stat, player, range_1, range_2):
        """get a error message when the stat is not in the correct value range"""
        message = Message(f"error", f"{stat} of {player} is not in range {range_1} and {range_2}")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return json_rep


class CheckPermissions(APIView):
    def get(self, request):
        """checks if the user sent has the right permissions to get the data"""
        _, json_message, response_status = check_authorization(request)
        return Response(json_message, status=response_status)
