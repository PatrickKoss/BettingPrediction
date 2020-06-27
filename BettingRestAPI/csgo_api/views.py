import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from BettingRestAPI.Helper.CSGOHelper import check_authorization
from BettingRestAPI.Serializer.CSGOSerializer import MatchSerializer, TeamSerializer, TeamsPredictionSerializer
from BettingRestAPI.Serializer.Encoder import ComplexEncoder
from csgo_api.models import MatchResult, Match, Team
from BettingRestAPI.utils.Message import Message


class GetUpcomingMatches(APIView):
    def get(self, request):
        check, json_message, status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Upcoming Matches")
            upcoming_matches = Match.objects.filter(
                date__range=(datetime.now(), datetime.now() + timedelta(days=15))).order_by("date")
            upcoming_matches = MatchSerializer(upcoming_matches, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)


class GetMatchResult(APIView):
    def get(self, request):
        check, json_message, status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            upcoming_matches = Match.objects.all().order_by("-date")
            matches_result = MatchResult.objects.all().order_by("-date")
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
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)


class GetMatchResultStats(APIView):
    def get(self, request):
        check, json_message, status = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Match Results")
            upcoming_matches = Match.objects.all()
            matches_result = MatchResult.objects.all()
            df_matches_result = pd.DataFrame(list(matches_result.values()))
            df_upcoming_matches = pd.DataFrame(list(upcoming_matches.values()))
            df_upcoming_matches.drop(columns=["id"], inplace=True)
            df_matches_result.drop(columns=["id"], inplace=True)
            df_result = df_matches_result.merge(df_upcoming_matches, left_on=["Team_1_id", "Team_2_id", "date"],
                                                right_on=["Team_1_id", "Team_2_id", "date"], how="inner")
            df_result = df_result[(df_result["odds_team_1"] <= 4.5) & (df_result["odds_team_2"] <= 4.5)]
            # first set odds, sec threshold,
            result = []
            for odd in np.arange(1, 1.9, 0.02):
                odd = round(odd, 2)
                df = self.get_df_with_threshold(df_result.copy(), 0.51)
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                df = self.get_df_with_money(df)
                if len(df) == 0:
                    continue
                if len(df) < len(df_result) * 0.3:
                    continue
                roi = self.get_roi(df)
                average_odds = self.get_average_odds(df)
                result.append(
                    {"mode": f"odds: {odd}, mode: all", "accuracy": self.get_accuracy(df),
                         "roi": roi, "sampleSize": len(df), "averageOdds": average_odds})

            for odd in np.arange(1, 1.9, 0.02):
                odd = round(odd, 2)
                df = df_result[df_result["mode"] == "BO3"].copy()
                df = self.get_df_with_threshold(df, 0.51)
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                df = self.get_df_with_money(df)
                if len(df) == 0:
                    continue
                if len(df) < len(df_result) * 0.3:
                    continue
                roi = self.get_roi(df)
                average_odds = self.get_average_odds(df)
                result.append(
                    {"mode": f"odds: {odd}, mode: BO3", "accuracy": self.get_accuracy(df),
                     "roi": roi, "sampleSize": len(df), "averageOdds": average_odds})

            for odd in np.arange(1, 1.9, 0.02):
                odd = round(odd, 2)
                df = df_result[df_result["mode"] == "BO3"].copy()
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                df = self.get_df_with_money_svm(df)
                if len(df) == 0:
                    continue
                if len(df) < len(df_result) * 0.3:
                    continue
                roi = self.get_roi(df)
                average_odds = self.get_average_odds(df)
                result.append(
                    {"mode": f"odds: {odd}, mode: BO3, svm: true", "accuracy": self.get_accuracy(df),
                     "roi": roi, "sampleSize": len(df), "averageOdds": average_odds})

            for odd in np.arange(1, 1.9, 0.02):
                odd = round(odd, 2)
                df = df_result.copy()
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                df = self.get_df_with_money_svm(df)
                if len(df) == 0:
                    continue
                if len(df) < len(df_result) * 0.3:
                    continue
                roi = self.get_roi(df)
                average_odds = self.get_average_odds(df)
                result.append(
                    {"mode": f"odds: {odd}, mode: all, svm: true", "accuracy": self.get_accuracy(df),
                     "roi": roi, "sampleSize": len(df), "averageOdds": average_odds})

            result = sorted(result, key=lambda k: k["sampleSize"], reverse=True)

            json_rep = json.dumps({'message': message.repr_json(),
                                   'stats': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)

    def get_df_with_threshold(self, df, threshold):
        return df[((df["team_1_confidence"] > threshold) & (df["team_1_confidence"] >= df["team_2_confidence"])) | (
          (df["team_2_confidence"] > threshold) & (df["team_2_confidence"] >
                                                   df["team_1_confidence"]))]

    def get_df_with_money(self, df):
        df["money"] = df.apply(lambda row: row.odds_team_1 - 1 if row.team_1_win == 1
                                                              and row.team_1_confidence >= row.team_2_confidence
        else row.odds_team_2 - 1 if row.team_2_win == 1 and row.team_1_confidence < row.team_2_confidence else -1,
                               axis=1)
        return df

    def get_roi(self, df):
        return round(float((df["money"].sum()) / len(df)), 2)

    def get_accuracy(self, df):
        return round(float(len(df[df["money"] >= 0]) / len(df)), 2)

    def get_df_odds_threshold(self, df, odds):
        return df[(df["odds_team_1"] >= odds) & (df["odds_team_2"] >= odds)]

    def get_df_with_money_svm(self, df):
        df["money"] = df.apply(lambda row: row.odds_team_1 - 1 if row.team_1_win == 1
                                                              and row.prediction_svm == 0
        else row.odds_team_2 - 1 if row.team_2_win == 1 and row.prediction_svm == 1 else -1,
                               axis=1)
        return df

    def get_average_odds(self, df):
        filter_team_1_df = df[df["team_1_win"] == 1]
        result_array = np.array([filter_team_1_df["odds_team_1"]])
        filter_team_2_df = df[df["team_2_win"] == 1]
        result_array = np.concatenate((result_array, np.array([filter_team_2_df["odds_team_2"]])), axis=1)
        average_odds = sum(result_array[0]) / len(result_array[0])
        average_odds = round(float(average_odds), 2)
        return average_odds


class GetTeam(APIView):
    def get(self, request, id):
        check, json_message, status = check_authorization(request)
        if check:
            message = Message("success", f"Here is the Team")
            team = Team.objects.get(id=id)
            team = TeamSerializer(team, context={'request': request}).data
            json_rep = json.dumps({'message': message.repr_json(), 'team': team},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)


class GetTeams(APIView):
    def get(self, request):
        check, json_message, status = check_authorization(request)
        if check:
            message = Message("success", f"Here are the teams")
            teams = Team.objects.all().order_by("end_date")
            team_set = list({team.name: team for team in teams}.values())
            team_set.sort(key=lambda x: x.name)
            teams = TeamsPredictionSerializer(team_set, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'teams': teams},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)


class CreatePrediction(APIView):
    def post(self, request):
        check, json_message, status = check_authorization(request)
        if check:
            data = json.loads(request.body)
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
            if data["mode"] == "BO1":
                prediction_model = settings.PREDICTION_MODEL_ALL_WINS
                prediction_model_svm = settings.PREDICTION_MODEL_SVM_ALL_WINS
            else:
                prediction_model = settings.PREDICTION_MODEL_BO3_WINS
                prediction_model_svm = settings.PREDICTION_MODEL_SVM_BO3_WINS
            prediction_svm = prediction_model_svm.predict(prediction_array)
            team_2_confidence = round(prediction_model.predict(prediction_array)[0][0], 3)
            team_1_confidence = round(1 - team_2_confidence, 3)
            team_1_confidence = team_1_confidence.item()
            team_2_confidence = team_2_confidence.item()
            team_2_confidence = round(team_2_confidence, 3)
            team_1_confidence = round(team_1_confidence, 3)
            json_rep = json.dumps({'message': message.repr_json(),
                                   'prediction': {"team_1_confidence": team_1_confidence,
                                                  "team_2_confidence": team_2_confidence,
                                                  "prediction_svm": prediction_svm[0]}},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep, status=status)
        else:
            return Response(json_message, status=status)

    def get_player_stats_array(self, player):
        return np.array([[player["dpr"], player["kast"], player["impact"], player["adr"], player["kpr"]]])

    def get_team_player_array(self, player1, player2, player3, player4, player5):
        team_player_array = self.get_player_stats_array(player1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player2)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player3)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player4)), axis=1)
        return np.concatenate((team_player_array, self.get_player_stats_array(player5)), axis=1)


class CheckPermissions(APIView):
    def get(self, request):
        _, json_message, status = check_authorization(request)
        return Response(json_message, status=status)
