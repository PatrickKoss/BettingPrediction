from datetime import datetime, timedelta

from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient

from BettingRestAPI.Serializer.CSGOSerializer import MatchSerializer, MatchResultSerializer, TeamsPredictionSerializer, \
    TeamSerializer


# Create your tests here.
class CheckPermissions(APITestCase):
    def setUp(self) -> None:
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        if not User.objects.filter(username="User2").exists():
            self.logged_in_user = User.objects.create_user(username="User2", password="secret", email="user2@gmail.com")
            self.logged_in_token, _ = Token.objects.get_or_create(user=self.logged_in_user)

        self.client = RequestsClient()
        self.maxDiff = None

    def test_no_authentication_sent(self):
        response = self.client.get('http://127.0.0.1:8000/csgo/check-permissions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_authentication_sent(self):
        self.client.headers.update({"Authorization": "asdfasdf"})
        response = self.client.get('http://127.0.0.1:8000/csgo/check-permissions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_permission(self):
        self.client.headers.update({"Authorization": self.logged_in_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/check-permissions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_right_permission(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/check-permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUpcomingMatches(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_empty(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/upcoming-matches/')
        self.assertEqual(response.json()["upcoming_matches"], [])

    def test_single_valid(self):
        players = mommy.make("Player", _quantity=5)
        for player in players:
            player.save()
        teams = mommy.make("Team", _quantity=2)
        for team in teams:
            team.save()
        match = mommy.make("Match", date=(datetime.now() + timedelta(days=1)))
        match.save()
        match = MatchSerializer(match).data
        match.update({
            "nnPickedTeam": match["Team_1"]["name"] if match["team_1_confidence"] >= match["team_2_confidence"]
            else match["Team_2"]["name"]})
        match.update({
            "svmPickedTeam": match["Team_1"]["name"] if float(match["prediction_svm"]) == 0 else match["Team_2"][
                "name"]})
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/upcoming-matches/')
        self.assertEqual(response.json()["upcoming_matches"][0], match)

    def test_one_past_one_present(self):
        players = mommy.make("Player", _quantity=5)
        for player in players:
            player.save()
        teams = mommy.make("Team", _quantity=2)
        for team in teams:
            team.save()
        match_1 = mommy.make("Match", date=(datetime.now() + timedelta(days=1)))
        match_1.save()
        match_2 = mommy.make("Match", date=(datetime.now() - timedelta(days=1)))
        match_2.save()
        match_1 = MatchSerializer(match_1).data
        match_1.update({
            "nnPickedTeam": match_1["Team_1"]["name"] if match_1["team_1_confidence"] >= match_1["team_2_confidence"]
            else match_1["Team_2"]["name"]})
        match_1.update({
            "svmPickedTeam": match_1["Team_1"]["name"] if float(match_1["prediction_svm"]) == 0 else match_1["Team_2"][
                "name"]})
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/upcoming-matches/')
        self.assertEqual(response.json()["upcoming_matches"], [match_1])

    def test_4_present_matches(self):
        players = mommy.make("Player", _quantity=5)
        for player in players:
            player.save()
        teams = mommy.make("Team", _quantity=2)
        for team in teams:
            team.save()
        match_1 = mommy.make("Match", date=(datetime.now() + timedelta(days=1)), _quantity=4)
        for match in match_1:
            match.save()
        match_2 = mommy.make("Match", date=(datetime.now() - timedelta(days=1)))
        match_2.save()
        match_1 = MatchSerializer(match_1, many=True).data
        for match in match_1:
            match.update({
                "nnPickedTeam": match["Team_1"]["name"] if match["team_1_confidence"] >= match["team_2_confidence"]
                else match["Team_2"]["name"]})
            match.update({
                "svmPickedTeam": match["Team_1"]["name"] if float(match["prediction_svm"]) == 0 else match["Team_2"][
                    "name"]})
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/upcoming-matches/')
        self.assertEqual(response.json()["upcoming_matches"], match_1)


class TestMatchResult(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_empty(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/results/')
        self.assertEqual(response.json()["matchResult"], [])

    def test_valid(self):
        player = mommy.make("Player")
        player.save()
        team = mommy.make("Team")
        team.save()
        date = datetime.now() - timedelta(days=1)
        match = mommy.make("Match", date=(date.isoformat() + "+00:00"))
        match.save()
        match = MatchSerializer(match).data
        match_result = mommy.make("MatchResult", date=match["date"])
        match_result.save()
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/csgo/results/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetTeam(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_no_number_id(self):
        player = mommy.make("Player")
        player.save()
        team = mommy.make("Team")
        team.save()
        team = TeamsPredictionSerializer(team).data
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/teams/asdf')
        self.assertEqual(response.json()["teams"], [team])

    def test_wrong_number_id(self):
        player = mommy.make("Player")
        player.save()
        team = mommy.make("Team")
        team.save()
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/teams/5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_id(self):
        player = mommy.make("Player")
        player.save()
        team = mommy.make("Team")
        team.save()
        team = TeamSerializer(team).data
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/teams/1')
        self.assertEqual(response.json()["team"], team)


class TestGetTeams(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_empty(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/teams/')
        self.assertEqual(response.json()["teams"], [])

    def test_valid(self):
        player = mommy.make("Player")
        player.save()
        team = mommy.make("Team")
        team.save()
        team = TeamsPredictionSerializer(team).data
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/teams/')
        self.assertEqual(response.json()["teams"], [team])


class TestCreatePrediction(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None
        players = mommy.make("Player", _quantity=10, adr=50, dpr=0.2, kpr=0.8, impact=1, kast=0.5)
        for player in players:
            player.save()
        team_1 = mommy.make("Team", winning_percentage=0.5)
        team_1.save()
        team_2 = mommy.make("Team", winning_percentage=0.5)
        team_2.save()
        self.team_1 = TeamSerializer(team_1).data
        self.team_2 = TeamSerializer(team_2).data

    def test_empty(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_team(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/', json={"team_1": self.team_1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_player(self):
        team_1_copy = self.team_1.copy()
        del team_1_copy["Player_1"]
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_attribute_in_player(self):
        team_1_copy = self.team_1.copy()
        del team_1_copy["Player_1"]["adr"]
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_adr(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["adr"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_kpr(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["kpr"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_dpr(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["dpr"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_impact(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["impact"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_kast(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["kast"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_team_winning_percentage(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["winning_percentage"] = "asdf"
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_adr_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["adr"] = -10.0
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_kpr_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["kpr"] = 1000.0
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_dpr_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["dpr"] = 3000.0
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_impact_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["impact"] = -10.0
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_player_kast_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["Player_1"]["kast"] = 20
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_attribute_in_team_winning_percentage_value(self):
        team_1_copy = self.team_1.copy()
        team_1_copy["winning_percentage"] = 2
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": team_1_copy, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_data(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/csgo/predictions/',
                                    json={"team_1": self.team_1, "team_2": self.team_2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPredictionStats(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None
        players = mommy.make("Player", _quantity=10, adr=50, dpr=0.2, kpr=0.8, impact=1, kast=0.5)
        for player in players:
            player.save()
        team_1 = mommy.make("Team", winning_percentage=0.5)
        team_1.save()
        team_2 = mommy.make("Team", winning_percentage=0.5)
        team_2.save()
        self.team_1 = TeamSerializer(team_1).data
        self.team_2 = TeamSerializer(team_2).data
        today = datetime.now()
        upcoming_match = mommy.make("Match", odds_team_1=1, odds_team_2=1, team_1_confidence=1, team_2_confidence=0,
                                    prediction_svm=0, _quantity=15, date=today)
        for match in upcoming_match:
            match.save()
        upcoming_match = mommy.make("Match", odds_team_1=1, odds_team_2=1, team_1_confidence=0, team_2_confidence=1,
                                    prediction_svm=1, _quantity=5, date=today)
        for match in upcoming_match:
            match.save()
        match_result = mommy.make("MatchResult", team_1_win=1, team_2_win=2, date=today, _quantity=20)
        for match in match_result:
            match.save()

    def test_valid(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get(f'http://127.0.0.1:8000/csgo/results-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
