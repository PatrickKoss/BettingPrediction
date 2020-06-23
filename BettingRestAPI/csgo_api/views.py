import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from rest_framework.response import Response
from rest_framework.views import APIView

from BettingRestAPI.Helper.CSGOHelper import check_authorization
from BettingRestAPI.Serializer.CSGOSerializer import MatchSerializer, TeamSerializer, TeamsPredictionSerializer
from BettingRestAPI.Serializer.Encoder import ComplexEncoder
from csgo_api.models import MatchResult, Match, Team
from user.utils.Message import Message
from django.conf import settings


class GetUpcomingMatches(APIView):
    def get(self, request):
        check, json_message = check_authorization(request)
        if check:
            message = Message("success", f"CSGO Upcoming Matches")
            upcoming_matches = Match.objects.filter(
                date__range=(datetime.now(), datetime.now() + timedelta(days=15))).order_by("date")
            upcoming_matches = MatchSerializer(upcoming_matches, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        else:
            return Response(json_message)


class GetMatchResult(APIView):
    def get(self, request):
        check, json_message = check_authorization(request)
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
            return Response(json_rep)
        else:
            return Response(json_message)


class GetMatchResultStats(APIView):
    def get(self, request):
        check, json_message = check_authorization(request)
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
            # first set odds, sec threshold,
            result = []
            for odd in np.arange(1, 1.9, 0.01):
                odd = round(odd, 2)
                df = self.get_df_with_threshold(df_result, 0.51)
                df = self.get_df_odds_threshold(df, odd)
                if len(df) == 0:
                    continue
                df = self.get_df_with_money(df)
                if len(df) == 0:
                    continue
                roi = self.get_roi(df)
                # if roi <= 0:
                #     continue
                result.append(
                    {"mode": f"odds_{odd}", "accuracy": self.get_accuracy(df),
                     "roi": roi, "sampleSize": len(df)})
            result = sorted(result, key=lambda k: k["roi"])

            json_rep = json.dumps({'message': message.repr_json(),
                                   'stats': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        else:
            return Response(json_message)

    def get_df_with_threshold(self, df, threshold):
        return df[((df["team_1_confidence"] > threshold) & (df["team_1_confidence"] >= df["team_2_confidence"])) | (
          (df["team_2_confidence"] > threshold) & (df["team_2_confidence"] >
                                                   df["team_1_confidence"]))]

    def get_df_with_money(self, df):
        df["money"] = df.apply(lambda row: row.odds_team_1 if row.team_1_win == 1
                                                              and row.team_1_confidence >= row.team_2_confidence
        else row.odds_team_2 if row.team_2_win == 1 and row.team_1_confidence < row.team_2_confidence else -1,
                               axis=1)
        return df

    def get_roi(self, df):
        return round(float((df["money"].sum() - len(df)) / len(df)), 2)

    def get_accuracy(self, df):
        return round(float(len(df[df["money"] > 0]) / len(df)), 2)

    def get_df_odds_threshold(self, df, odds):
        return df[(df["odds_team_1"] >= odds) & (df["odds_team_2"] >= odds)]


class GetTeam(APIView):
    def get(self, request, id):
        check, json_message = check_authorization(request)
        if check:
            message = Message("success", f"Here is the Team")
            team = Team.objects.get(id=id)
            team = TeamSerializer(team, context={'request': request}).data
            json_rep = json.dumps({'message': message.repr_json(), 'team': team},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        else:
            return Response(json_message)


class GetTeams(APIView):
    def get(self, request):
        check, json_message = check_authorization(request)
        if check:
            message = Message("success", f"Here are the teams")
            teams = Team.objects.all().order_by("end_date")
            team_set = list({team.name: team for team in teams}.values())
            team_set.sort(key=lambda x: x.name)
            teams = TeamsPredictionSerializer(team_set, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'teams': teams},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        else:
            return Response(json_message)


class CreatePrediction(APIView):
    def post(self, request):
        check, json_message = check_authorization(request)
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
            else:
                prediction_model = settings.PREDICTION_MODEL_BO3_WINS
            team_2_confidence = round(prediction_model.predict(prediction_array)[0][0], 3)
            team_1_confidence = round(1 - team_2_confidence, 3)
            team_1_confidence = team_1_confidence.item()
            team_2_confidence = team_2_confidence.item()
            team_2_confidence = round(team_2_confidence, 3)
            team_1_confidence = round(team_1_confidence, 3)
            json_rep = json.dumps({'message': message.repr_json(),
                                   'prediction': {"team_1_confidence": team_1_confidence,
                                                  "team_2_confidence": team_2_confidence}},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        else:
            return Response(json_message)

    def get_player_stats_array(self, player):
        return np.array([[player["dpr"], player["kast"], player["impact"], player["adr"], player["kpr"]]])

    def get_team_player_array(self, player1, player2, player3, player4, player5):
        team_player_array = self.get_player_stats_array(player1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player2)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player3)), axis=1)
        team_player_array = np.concatenate((team_player_array, self.get_player_stats_array(player4)), axis=1)
        return np.concatenate((team_player_array, self.get_player_stats_array(player5)), axis=1)
