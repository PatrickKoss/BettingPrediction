import json
from datetime import datetime, timedelta

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
            upcoming_matches = Match.objects.filter(date__range=(datetime.now(), datetime.now() + timedelta(days=15)))
            upcoming_matches = MatchSerializer(upcoming_matches)
            json_rep = json.dumps({'message': message.repr_json(), 'upcoming_matches': upcoming_matches},
                                  cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)

        return Response(json_rep)


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
    class Meta:
        model = Team
        fields = ['name', 'winning_percentage', 'Player_1', 'Player_2', 'Player_3', 'Player_4', 'Player_5',
                  'start_date', 'end_date']


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Match
        fields = ['date', 'Team_1', 'Team_2', 'odds_team_1', 'odds_team_2', 'team_1_confidence', 'team_2_confidence',
                  'mode']


class MatchResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchResult
        fields = ['date', 'Team_1', 'Team_2', 'team_1_win', 'team_2_win']
