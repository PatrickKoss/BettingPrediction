# Generated by Django 3.0.2 on 2020-06-18 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csgo_api', '0005_matchresult_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matchresult',
            name='mode',
        ),
        migrations.RemoveField(
            model_name='matchresult',
            name='team_1_prediction',
        ),
        migrations.RemoveField(
            model_name='matchresult',
            name='team_2_prediction',
        ),
    ]