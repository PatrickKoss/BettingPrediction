from rest_framework import serializers

from csgo_api.models import Player, Team, MatchResult, Match


# Serializers define the API representation.
class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ['name', 'dpr', 'kast', 'impact', 'adr', 'kpr']


class TeamSerializerUpcomingMatches(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'id']


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    Team_1 = TeamSerializerUpcomingMatches()
    Team_2 = TeamSerializerUpcomingMatches()

    class Meta:
        model = Match
        fields = ['date', 'Team_1', 'Team_2', 'odds_team_1', 'odds_team_2', 'team_1_confidence', 'team_2_confidence',
                  'mode']


class MatchResultSerializer(serializers.HyperlinkedModelSerializer):
    Team_1 = TeamSerializerUpcomingMatches()
    Team_2 = TeamSerializerUpcomingMatches()

    class Meta:
        model = MatchResult
        fields = ['date', 'Team_1', 'Team_2', 'team_1_win', 'team_2_win']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    Player_1 = PlayerSerializer()
    Player_2 = PlayerSerializer()
    Player_3 = PlayerSerializer()
    Player_4 = PlayerSerializer()
    Player_5 = PlayerSerializer()

    class Meta:
        model = Team
        fields = ['name', 'id', 'winning_percentage', 'Player_1', 'Player_2', 'Player_3', 'Player_4', 'Player_5']


class TeamsPredictionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'id']
