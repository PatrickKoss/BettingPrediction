import json
from datetime import datetime, timedelta
from threading import Thread

import numpy as np
from django.conf import settings
from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from BettingRestAPI.Helper.CSGOHelper import check_authorization
from BettingRestAPI.Serializer.CSGOSerializer import MatchSerializer, TeamSerializer, TeamsPredictionSerializer
from BettingRestAPI.Serializer.Encoder import ComplexEncoder
from BettingRestAPI.utils.Message import Message
from csgo_api.models import Match, Team


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
                    "svmPickedTeam": match["Team_1"]["name"] if float(match["prediction_svm"]) == 0 else
                    match["Team_2"][
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
            with connection.cursor() as cursor:
                cursor.execute(f"select m.Team_1_id, m.Team_2_id, DATE(m.date) as date , m.team_1_win, m.team_2_win, "
                               f"m.odds_team_1, m.odds_team_2, m.team_1_confidence, m.team_2_confidence, m.prediction_svm, "
                               f"m.name as Team1, t.name as Team2, m.mode, "
                               f"CASE m.team_1_confidence >= m.team_2_confidence WHEN TRUE THEN m.name ELSE t.name END AS nnPickedTeam, "
                               f"CASE m.prediction_svm = 0 WHEN TRUE THEN m.name ELSE t.name END AS svmPickedTeam, "
                               f"CASE m.team_1_win = 1 WHEN TRUE THEN m.name ELSE t.name END AS winningTeam "
                               f"FROM (SELECT name, id FROM csgo_api_team) as t INNER JOIN ("
                               f"select m.Team_1_id, m.Team_2_id, m.date, m.team_1_win, m.team_2_win, "
                               f"m.odds_team_1, m.odds_team_2, m.team_1_confidence, m.team_2_confidence, m.prediction_svm, t.name, m.mode "
                               f"FROM (SELECT name, id FROM csgo_api_team) as t INNER JOIN ("
                               f"select m.Team_1_id, m.Team_2_id, m.date, mr.team_1_win, mr.team_2_win, "
                               f"m.odds_team_1, m.odds_team_2, m.team_1_confidence, m.team_2_confidence, m.prediction_svm, m.mode "
                               f"From csgo_api_matchResult as mr "
                               f"INNER JOIN csgo_api_match as m "
                               f"ON mr.Team_1_id = m.Team_1_id AND mr.Team_2_id = m.Team_2_id AND m.date = mr.date"
                               f") as m "
                               f"ON t.id = m.Team_1_id"
                               f") as m "
                               f"ON t.id = m.Team_2_id")
                columns = [col[0] for col in cursor.description]
                res = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'message': {"message": "fine", "messageType": "success"}, 'matchResult': res},
                            status=response_status)
        else:
            return Response(json_message, status=response_status)


class GetMatchResultStats(APIView):
    def get(self, request):
        """return json of stats that the model produces"""
        check, json_message, response_status = check_authorization(request)
        if check:
            result_list = []
            # multi threading is about 4 times faster than single threaded
            threads = [None] * 9
            results = [None] * 54
            threads_all = [None] * 9
            results_all = [None] * 18
            index_threads = 0
            index_results = 0
            index_threads_all = 0
            index_results_all = 0
            for odd in np.arange(1, 1.9, 0.1):
                odd = round(odd, 2)
                threads[index_threads] = Thread(target=self.get_query_dict_groups, args=(odd, results, index_results))
                threads[index_threads].start()
                index_threads += 1
                index_results += 6
                threads_all[index_threads_all] = Thread(target=self.get_query_dict_all,
                                                        args=(odd, results_all, index_results_all))
                threads_all[index_threads_all].start()
                index_threads_all += 1
                index_results_all += 2
            for i in range(len(threads)):
                threads[i].join()
            for i in range(len(threads_all)):
                threads_all[i].join()
            results = results + results_all
            results = sorted(results, key=lambda k: k["odds"])
            return Response({'message': {"message": "fine", "messageType": "success"}, 'stats': results},
                            status=response_status)
        else:
            return Response(json_message, status=response_status)

    def get_query_dict_groups(self, odd, results, index):
        with connection.cursor() as cursor:
            cursor.execute("select COUNT(id) as sampleSize, round(SUM(NN_Money)/COUNT(id),2) as roi_nn, "
                           "round(SUM(SVM_Money)/COUNT(id),2) as roi_svm, mode, "
                           "round(SUM(odds)/COUNT(id),2) as average_odds, "
                           "round(SUM(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END)/COUNT(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END)+1,2) as nn_winning_odds, "
                           "round(SUM(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END)/COUNT(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END)+1,2) as svm_winning_odds, "
                           "round(CAST(COUNT(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END) as double)/CAST(COUNT(id) as double),2) as nn_accuracy, "
                           "round(CAST(COUNT(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END) as double)/CAST(COUNT(id) as double),2) as svm_accuracy "
                           "FROM ("
                           f"select mr.id as id, m.mode as mode, "
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 AND m.team_1_confidence >= m.team_2_confidence THEN m.odds_team_1 - 1 "
                           f"WHEN mr.team_2_win = 1 AND m.team_1_confidence < m.team_2_confidence THEN m.odds_team_2 - 1 "
                           f"ELSE -1 END AS NN_Money,"
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 AND m.prediction_svm = 0 THEN m.odds_team_1 - 1 "
                           f"WHEN mr.team_2_win = 1 AND m.prediction_svm = 1 THEN m.odds_team_2 - 1 "
                           f"ELSE -1 END AS SVM_Money, "
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 THEN m.odds_team_1 "
                           f"WHEN mr.team_2_win = 1 THEN m.odds_team_2 "
                           f"ELSE 1 END AS odds "
                           f"From csgo_api_matchResult as mr "
                           f"INNER JOIN csgo_api_match as m "
                           f"ON mr.Team_1_id = m.Team_1_id AND mr.Team_2_id = m.Team_2_id AND m.date = mr.date "
                           f"WHERE m.odds_team_1 >= %s and m.odds_team_2 >= %s) "
                           f"GROUP BY mode", [odd, odd])

            columns = [col[0] for col in cursor.description]

            res = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for r in res:
                results[index] = {'accuracy': r["svm_accuracy"], 'roi': r["roi_svm"], 'sampleSize': r["sampleSize"],
                                  'averageOdds': r["average_odds"], 'svm': "SVM",
                                  'mode': r["mode"], 'odds': odd, 'average_winning_odds': r["svm_winning_odds"]}
                results[index + 1] = {'accuracy': r["nn_accuracy"], 'roi': r["roi_nn"], 'sampleSize': r["sampleSize"],
                                      'averageOdds': r["average_odds"], 'svm': "NN",
                                      'mode': r["mode"], 'odds': odd, 'average_winning_odds': r["nn_winning_odds"]}
                index += 2

    def get_query_dict_all(self, odd, results, index):
        with connection.cursor() as cursor:
            cursor.execute("select COUNT(id) as sampleSize, round(SUM(NN_Money)/COUNT(id),2) as roi_nn, "
                           "round(SUM(SVM_Money)/COUNT(id),2) as roi_svm, mode, "
                           "round(SUM(odds)/COUNT(id),2) as average_odds, "
                           "round(SUM(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END)/COUNT(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END)+1,2) as nn_winning_odds, "
                           "round(SUM(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END)/COUNT(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END)+1,2) as svm_winning_odds, "
                           "round(CAST(COUNT(CASE NN_Money > 0 WHEN TRUE THEN NN_Money END) as double)/CAST(COUNT(id) as double),2) as nn_accuracy, "
                           "round(CAST(COUNT(CASE SVM_Money > 0 WHEN TRUE THEN SVM_Money END) as double)/CAST(COUNT(id) as double),2) as svm_accuracy "
                           "FROM ("
                           f"select mr.id as id, m.mode as mode, "
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 AND m.team_1_confidence >= m.team_2_confidence THEN m.odds_team_1 - 1 "
                           f"WHEN mr.team_2_win = 1 AND m.team_1_confidence < m.team_2_confidence THEN m.odds_team_2 - 1 "
                           f"ELSE -1 END AS NN_Money,"
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 AND m.prediction_svm = 0 THEN m.odds_team_1 - 1 "
                           f"WHEN mr.team_2_win = 1 AND m.prediction_svm = 1 THEN m.odds_team_2 - 1 "
                           f"ELSE -1 END AS SVM_Money, "
                           f"CASE "
                           f"WHEN mr.team_1_win = 1 THEN m.odds_team_1 "
                           f"WHEN mr.team_2_win = 1 THEN m.odds_team_2 "
                           f"ELSE 1 END AS odds "
                           f"From csgo_api_matchResult as mr "
                           f"INNER JOIN csgo_api_match as m "
                           f"ON mr.Team_1_id = m.Team_1_id AND mr.Team_2_id = m.Team_2_id AND m.date = mr.date "
                           f"WHERE m.odds_team_1 >= %s and m.odds_team_2 >= %s) "
                           f"", [odd, odd])
            columns = [col[0] for col in cursor.description]
            res = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for r in res:
                results[index] = {'accuracy': r["svm_accuracy"], 'roi': r["roi_svm"], 'sampleSize': r["sampleSize"],
                                  'averageOdds': r["average_odds"], 'svm': "SVM",
                                  'mode': "all games", 'odds': odd, 'average_winning_odds': r["svm_winning_odds"]}
                results[index + 1] = {'accuracy': r["nn_accuracy"], 'roi': r["roi_nn"], 'sampleSize': r["sampleSize"],
                                      'averageOdds': r["average_odds"], 'svm': "NN",
                                      'mode': "all games", 'odds': odd, 'average_winning_odds': r["nn_winning_odds"]}
                index += 2


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
