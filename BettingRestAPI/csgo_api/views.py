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
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Upcoming Matches")
            upcoming_matches = Match.objects.filter(
                date__range=(datetime.now(), datetime.now() + timedelta(days=15))).order_by("date")
            upcoming_matches = MatchSerializer(upcoming_matches, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetMatchResult(APIView):
    def get(self, request):
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            matches_result = MatchResult.objects.all().order_by("-date")
            if len(matches_result) == 0:
                json_rep = json.dumps({'message': message.repr_json(), 'matchResult': []},
                                      cls=ComplexEncoder)
                json_rep = json.loads(json_rep)
                return Response(json_rep, status=response_status)
            upcoming_matches = Match.objects.all().order_by("-date")
            df_matches_result = pd.DataFrame(list(matches_result.values()))
            df_upcoming_matches = pd.DataFrame(list(upcoming_matches.values()))
            df_upcoming_matches.drop(columns=["id"], inplace=True)
            df_matches_result.drop(columns=["id"], inplace=True)
            df_result = df_matches_result.merge(df_upcoming_matches, left_on=["Team_1_id", "Team_2_id", "date"],
                                                right_on=["Team_1_id", "Team_2_id", "date"], how="inner")
            df_result["team_1_win"] = df_result["team_1_win"].astype(float)
            df_result["team_2_win"] = df_result["team_2_win"].astype(float)
            df_result["odds_team_1"] = df_result["odds_team_1"].astype(float)
            df_result["odds_team_2"] = df_result["odds_team_2"].astype(float)
            df_result["team_1_confidence"] = df_result["team_1_confidence"].astype(float)
            df_result["team_2_confidence"] = df_result["team_2_confidence"].astype(float)
            df_result["prediction_svm"] = df_result["prediction_svm"].astype(float)
            result = df_result.to_dict('records')
            for d in result:
                match = upcoming_matches.filter(date=d["date"], Team_1_id=d["Team_1_id"],
                                                Team_2_id=d["Team_2_id"]).first()
                team_1_name = match.Team_1.name
                team_2_name = match.Team_2.name
                d.update({"Team1": team_1_name, "Team2": team_2_name, "date": d["date"].isoformat()})
            json_rep = json.dumps({'message': message.repr_json(), 'matchResult': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetMatchResultStats(APIView):
    def get(self, request):
        check, json_message, response_status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            matches_result = MatchResult.objects.all()
            upcoming_matches = Match.objects.all()
            df_matches_result = pd.DataFrame(list(matches_result.values()))
            df_upcoming_matches = pd.DataFrame(list(upcoming_matches.values()))
            df_upcoming_matches.drop(columns=["id"], inplace=True)
            df_matches_result.drop(columns=["id"], inplace=True)
            df_result = df_matches_result.merge(df_upcoming_matches, left_on=["Team_1_id", "Team_2_id", "date"],
                                                right_on=["Team_1_id", "Team_2_id", "date"], how="inner")
            df_result = df_result[(df_result["odds_team_1"] <= 4.5) & (df_result["odds_team_2"] <= 4.5)]
            # first set odds, sec threshold,
            result = []
            self.create_result_list(df_result, result, False)
            self.create_result_list(df_result, result, False, "BO1")
            self.create_result_list(df_result, result, False, "BO3")
            self.create_result_list(df_result, result, True)
            self.create_result_list(df_result, result, True, "BO1")
            self.create_result_list(df_result, result, True, "BO3")

            result = sorted(result, key=lambda k: k["sampleSize"], reverse=True)

            json_rep = json.dumps({'message': message.repr_json(),
                                   'stats': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=response_status)
        else:
            return Response(json_message, status=response_status)

    def get_df_with_threshold(self, df, threshold):
        return df[((df["team_1_confidence"] > threshold) & (df["team_1_confidence"] >= df["team_2_confidence"])) | (
          (df["team_2_confidence"] > threshold) & (df["team_2_confidence"] >
                                                   df["team_1_confidence"]))]

    def get_df_with_money(self, df, odd_reduction=0):
        df["money"] = df.apply(lambda row: (float(row.odds_team_1) - 1 - odd_reduction) if row.team_1_win == 1
                                                                                           and row.team_1_confidence >= row.team_2_confidence
        else (float(
            row.odds_team_2) - 1) if row.team_2_win == 1 and row.team_1_confidence < row.team_2_confidence else -1,
                               axis=1)
        return df

    def get_roi(self, df):
        return round(float((df["money"].sum()) / len(df)), 2)

    def get_accuracy(self, df):
        return round(float(len(df[df["money"] >= 0]) / len(df)), 2)

    def get_df_odds_threshold(self, df, odds):
        """return a data frame with a given odds threshold"""
        return df[(df["odds_team_1"] >= odds) & (df["odds_team_2"] >= odds)]

    def get_df_with_money_svm(self, df, odd_reduction=0):
        """return a data frame with the money made on a bet"""
        df["money"] = df.apply(lambda row: (float(row.odds_team_1) - 1 - odd_reduction) if row.team_1_win == 1
                                                                           and row.prediction_svm == 0
        else (float(row.odds_team_2) - 1) if row.team_2_win == 1 and row.prediction_svm == 1 else -1,
                               axis=1)
        return df

    def get_average_odds(self, df, odd_reduction=0):
        """This method calculates the average odds of all bets"""
        filter_team_1_df = df[df["team_1_win"] == 1]
        result_array = np.array([filter_team_1_df["odds_team_1"]])
        filter_team_2_df = df[df["team_2_win"] == 1]
        result_array = np.concatenate((result_array, np.array([filter_team_2_df["odds_team_2"]])), axis=1)
        average_odds = sum(result_array[0]) / len(result_array[0])
        average_odds = round(round(float(average_odds), 2) - odd_reduction, 2)
        return average_odds

    def create_result_list(self, df_result, result, svm, mode=None):
        df_copy = df_result.copy()
        if mode is not None:
            df_copy = df_result[df_result["mode"] == mode]
        for odd in np.arange(1, 1.9, 0.1):
            for odd_reduction in np.arange(0, 0.5, 0.1):
                odd = round(odd, 2)
                odd_reduction = round(odd_reduction, 2)
                if not svm:
                    df = self.get_df_with_threshold(df_copy, 0.5001)
                else:
                    df = df_copy.copy()
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                if svm:
                    df = self.get_df_with_money_svm(df, odd_reduction)
                else:
                    df = self.get_df_with_money(df, odd_reduction)
                if len(df) == 0:
                    continue
                if len(df) < len(df_result) * 0.3:
                    continue
                roi = self.get_roi(df)
                average_odds = self.get_average_odds(df, odd_reduction)
                if mode is None:
                    mode_selected = "all games"
                else:
                    mode_selected = mode
                if svm:
                    model = "SVM"
                else:
                    model = "NN"
                result.append(
                    {"accuracy": self.get_accuracy(df),
                     "roi": roi, "sampleSize": len(df), "averageOdds": average_odds, "svm": model,
                     "mode": mode_selected,
                     "odds": odd, "odds_reduction": odd_reduction})


class GetTeam(APIView):
    def get(self, request, id):
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
        check, json_message, response_status = check_authorization(request)
        if check:
            data = json.loads(request.body or "{}")
            check_teams, response = self.check_teams(data)
            if not check_teams:
                return response
            check_player_team_1, response = self.check_players_in_team(data, "team_1")
            if not check_player_team_1:
                return response
            check_player_team_2, response = self.check_players_in_team(data, "team_1")
            if not check_player_team_2:
                return response
            check_players, response = self.check_players(data)
            if not check_players:
                return response
            validate_data, response = self.validate_data(data)
            if not validate_data:
                return response

            message = Message("success", f"Prediction")
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
        return np.array([[player["dpr"], player["kast"], player["impact"], player["adr"], player["kpr"]]])

    def get_team_player_array(self, player1, player2, player3, player4, player5):
        team_player_array = self.get_player_stats_array(player1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player2)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player3)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player4)), axis=1)
        return np.concatenate((team_player_array, self.get_player_stats_array(player5)), axis=1)

    def check_teams(self, data):
        if "team_1" not in data or "team_2" not in data:
            message = Message("error", f"No teams sent")
            json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
        else:
            return True, ""

    def check_players_in_team(self, data, team):
        if "Player_1" not in data[team] or "Player_2" not in data[team] or "Player_3" not in data[
            team] or "Player_4" not in data[team] or "Player_5" not in data[team]:
            message = Message(f"error", f"No player for {team} sent")
            json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return False, Response(json_rep, status=status.HTTP_400_BAD_REQUEST)
        else:
            return True, ""

    def check_players(self, data):
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
        message = Message(f"error", f"{stat} of {player} is not of type float")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return json_rep

    def get_error_message_player_stat_in_range(self, stat, player, range_1, range_2):
        message = Message(f"error", f"{stat} of {player} is not in range {range_1} and {range_2}")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return json_rep


class CheckPermissions(APIView):
    def get(self, request):
        _, json_message, response_status = check_authorization(request)
        return Response(json_message, status=response_status)
