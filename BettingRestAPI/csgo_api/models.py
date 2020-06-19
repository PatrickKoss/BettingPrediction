from django.db import models


# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=200)
    dpr = models.DecimalField(decimal_places=2, max_digits=10)
    kast = models.DecimalField(decimal_places=2, max_digits=10)
    impact = models.DecimalField(decimal_places=2, max_digits=10)
    adr = models.DecimalField(decimal_places=2, max_digits=10)
    kpr = models.DecimalField(decimal_places=2, max_digits=10)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Team(models.Model):
    name = models.CharField(max_length=200)
    winning_percentage = models.DecimalField(decimal_places=2, max_digits=10)
    player_1 = models.ForeignKey(Player, default=1, verbose_name="Player_1", on_delete=models.CASCADE, name="Player_1",
                                 related_name="Player_1")
    player_2 = models.ForeignKey(Player, default=1, verbose_name="Player_2", on_delete=models.CASCADE, name="Player_2",
                                 related_name="Player_2")
    player_3 = models.ForeignKey(Player, default=1, verbose_name="Player_3", on_delete=models.CASCADE, name="Player_3",
                                 related_name="Player_3")
    player_4 = models.ForeignKey(Player, default=1, verbose_name="Player_4", on_delete=models.CASCADE, name="Player_4",
                                 related_name="Player_4")
    player_5 = models.ForeignKey(Player, default=1, verbose_name="Player_5", on_delete=models.CASCADE, name="Player_5",
                                 related_name="Player_5")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Match(models.Model):
    date = models.DateTimeField()
    team_1 = models.ForeignKey(Team, default=1, verbose_name="Team_1", on_delete=models.CASCADE, name="Team_1",
                               related_name="Team_1")
    team_2 = models.ForeignKey(Team, default=1, verbose_name="Team_2", on_delete=models.CASCADE, name="Team_2",
                               related_name="Team_2")
    odds_team_1 = models.DecimalField(decimal_places=2, max_digits=10, default=1)
    odds_team_2 = models.DecimalField(decimal_places=2, max_digits=10, default=1)
    team_1_confidence = models.DecimalField(decimal_places=2, max_digits=10, default=1)
    team_2_confidence = models.DecimalField(decimal_places=2, max_digits=10, default=1)
    mode = models.CharField(max_length=20, default="bo1")


class MatchResult(models.Model):
    date = models.DateTimeField()
    team_1 = models.ForeignKey(Team, default=1, verbose_name="Team_1", on_delete=models.CASCADE, name="Team_1",
                               related_name="Team_1_Result")
    team_2 = models.ForeignKey(Team, default=1, verbose_name="Team_2", on_delete=models.CASCADE, name="Team_2",
                               related_name="Team_2_Result")
    team_1_win = models.DecimalField(decimal_places=2, max_digits=10, default=1)
    team_2_win = models.DecimalField(decimal_places=2, max_digits=10, default=1)
