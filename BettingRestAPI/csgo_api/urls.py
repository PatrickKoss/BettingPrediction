from django.conf.urls import url

from . import views

app_name = 'csgo_api'

urlpatterns = [
    url(r'^upcomingMatches/', views.GetUpcomingMatches.as_view()),
    url(r'^matchResult/', views.GetMatchResult.as_view()),
    url(r'^matchResultStats/', views.GetMatchResultStats.as_view()),
    url(r'^teams/(?P<id>[0-9]+)$', views.GetTeam.as_view(), name='id'),
    url(r'^teams/', views.GetTeams.as_view()),
    url(r'^prediction/', views.CreatePrediction.as_view()),
    url(r'^checkPermissions/', views.CheckPermissions.as_view()),
]