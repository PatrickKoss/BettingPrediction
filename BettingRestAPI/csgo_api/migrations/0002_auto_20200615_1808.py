# Generated by Django 3.0.2 on 2020-06-15 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csgo_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='Team_1',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='Team_1', to='csgo_api.Team', verbose_name='Team_1'),
        ),
        migrations.AddField(
            model_name='match',
            name='Team_2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='Team_2', to='csgo_api.Team', verbose_name='Team_2'),
        ),
        migrations.AddField(
            model_name='match',
            name='odds_team_1',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AddField(
            model_name='match',
            name='odds_team_2',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
    ]