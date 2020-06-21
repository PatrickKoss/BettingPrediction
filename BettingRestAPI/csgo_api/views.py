import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from csgo_api.models import Player, Team, MatchResult, Match
from user.utils.Message import Message


class GetUpcomingMatches(APIView):
    def get(self, request):
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"CSGO Upcoming Matches")
        if user is None:
            message = Message("error", f"Not logged in")
        else:
            upcoming_matches = Match.objects.filter(
                date__range=(datetime.now(), datetime.now() + timedelta(days=15))).order_by("date")
            upcoming_matches = MatchSerializer(upcoming_matches, context={'request': request}, many=True).data
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)

        return Response(json_rep)


class GetMatchResult(APIView):
    def get(self, request):
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"CSGO Match Results")
        if user is None:
            message = Message("error", f"Not logged in")
        else:
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
            test = df_result.to_dict('records')
            for d in test:
                match = upcoming_matches.filter(date=d["date"], Team_1_id=d["Team_1_id"],
                                                Team_2_id=d["Team_2_id"]).first()
                team_1_name = match.Team_1.name
                team_2_name = match.Team_2.name
                d.update({"Team1": team_1_name, "Team2": team_2_name, "date": d["date"].isoformat()})
                d.pop("Team_1_id", None)
                d.pop("Team_2_id", None)
            json_rep = json.dumps({'message': message.repr_json(), 'matchResult': test},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)

        return Response(json_rep)


class GetMatchResultStats(APIView):
    def get(self, request):
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"CSGO Match Results")
        if user is None:
            message = Message("error", f"Not logged in")
        else:
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
            for odd in np.arange(1, 1.7, 0.02):
                for threshold in np.arange(0.5, 0.8, 0.02):
                    odd = round(odd, 2)
                    threshold = round(threshold, 2)
                    df = self.get_filtered_odds_df(df_result)
                    df = self.get_df_with_threshold(df, threshold)
                    df = self.get_df_odds_threshold(df, odd)
                    if len(df) == 0:
                        continue
                    df = self.get_df_with_money(df)
                    if len(df) == 0:
                        continue
                    roi = self.get_roi(df)
                    if roi <= 0:
                        continue
                    result.append(
                        {"mode": f"odds_{odd}_thresholdConfidence_{threshold}", "accuracy": self.get_accuracy(df),
                         "roi": roi, "sampleSize": len(df)})
            result = sorted(result, key=lambda k: k["roi"])

            json_rep = json.dumps({'message': message.repr_json(),
                                   'stats': result},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)

        return Response(json_rep)

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

    def get_filtered_odds_df(self, df):
        return df[(df["odds_team_1"] < 3) & (df["odds_team_2"] < 3)]


# complex encoder for complex object Message
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


# Serializers define the API representation.
class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ['name', 'dpr', 'kast', 'impact', 'adr', 'kpr', 'start_date', 'end_date']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    Player_1 = PlayerSerializer()
    Player_2 = PlayerSerializer()
    Player_3 = PlayerSerializer()
    Player_4 = PlayerSerializer()
    Player_5 = PlayerSerializer()

    class Meta:
        model = Team
        fields = ['name', 'winning_percentage', 'Player_1', 'Player_2', 'Player_3', 'Player_4', 'Player_5',
                  'start_date', 'end_date']


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    Team_1 = TeamSerializer()
    Team_2 = TeamSerializer()

    class Meta:
        model = Match
        fields = ['date', 'Team_1', 'Team_2', 'odds_team_1', 'odds_team_2', 'team_1_confidence', 'team_2_confidence',
                  'mode']


class MatchResultSerializer(serializers.HyperlinkedModelSerializer):
    Team_1 = TeamSerializer()
    Team_2 = TeamSerializer()

    class Meta:
        model = MatchResult
        fields = ['date', 'Team_1', 'Team_2', 'team_1_win', 'team_2_win']
