from django.conf.urls import url

from . import views

app_name = 'csgo_api'

urlpatterns = [
    url(r'^upcoming-matches/', views.GetUpcomingMatches.as_view()),
    url(r'^results/', views.GetMatchResult.as_view()),
    url(r'^results-stats/', views.GetMatchResultStats.as_view()),
    url(r'^teams/(?P<id>[0-9]+)$', views.GetTeam.as_view(), name='id'),
    url(r'^teams/', views.GetTeams.as_view()),
    url(r'^predictions/', views.CreatePrediction.as_view()),
    url(r'^check-permissions/', views.CheckPermissions.as_view()),
]