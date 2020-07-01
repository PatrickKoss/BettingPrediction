import os

import django
import numpy as np
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BettingRestAPI.settings')
django.setup()

from csgo_api.models import Match
from django.contrib.auth.models import User, Permission


def get_player_stats_array(player):
    return np.array([[player.dpr, player.kast, player.impact, player.adr, player.kpr]])


def get_team_player_array(player1, player2, player3, player4, player5):
    team_player_array = get_player_stats_array(player1)
    team_player_array = np.concatenate((team_player_array, get_player_stats_array(player2)), axis=1)
    team_player_array = np.concatenate((team_player_array, get_player_stats_array(player3)), axis=1)
    team_player_array = np.concatenate((team_player_array, get_player_stats_array(player4)), axis=1)
    return np.concatenate((team_player_array, get_player_stats_array(player5)), axis=1)


def get_prediction_array(data):
    prediction_array = np.array([[data.Team_1.winning_percentage]])
    prediction_array = np.concatenate((prediction_array,
                                       get_team_player_array(data.Team_1.Player_1,
                                                             data.Team_1.Player_2,
                                                             data.Team_1.Player_3,
                                                             data.Team_1.Player_4,
                                                             data.Team_1.Player_5)), axis=1)
    prediction_array = np.concatenate((prediction_array, np.array([[data.Team_2.winning_percentage]])),
                                      axis=1)
    prediction_array = np.concatenate((prediction_array,
                                       get_team_player_array(data.Team_2.Player_1,
                                                             data.Team_2.Player_2,
                                                             data.Team_2.Player_3,
                                                             data.Team_2.Player_4,
                                                             data.Team_2.Player_5)), axis=1)
    return prediction_array


def update():
    matches = Match.objects.all()
    for match in matches:
        prediction_array = get_prediction_array(match)
        prediction_model = settings.PREDICTION_MODEL_SVM_ALL_WINS
        prediction = prediction_model.predict(prediction_array)
        match.prediction_svm = prediction[0]
        match.save()


def get_average_odds():
    matches = Match.objects.all()
    picked_odds = []
    final_odds = []
    for match in matches:
        if match.team_1_confidence >= match.team_2_confidence:
            picked_odds.append(match.odds_team_1)
        else:
            picked_odds.append(match.odds_team_2)
    for odd in picked_odds:
        if odd <= 5:
            final_odds.append(odd)
    print(final_odds)
    average = sum(final_odds) / len(final_odds)
    print(average)


def check_permissions():
    permissions = Permission.objects.all()
    for permission in permissions:
        print(permission.name)

def update_prediction_confidence():
    matches = Match.objects.all()
    for match in matches:
        prediction_array = get_prediction_array(match)
        prediction_model = settings.PREDICTION_MODEL_ALL_WINS
        team_2_confidence = round(prediction_model.predict(prediction_array)[0][0], 4)
        team_1_confidence = round(1 - team_2_confidence, 4)
        team_1_confidence = team_1_confidence.item()
        team_2_confidence = team_2_confidence.item()
        match.team_1_confidence = team_1_confidence
        match.team_2_confidence = team_2_confidence
        match.save()


if __name__ == "__main__":
    # update()
    # get_average_odds()
    # check_permissions()
    update_prediction_confidence()
