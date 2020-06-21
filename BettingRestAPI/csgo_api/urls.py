from django.conf.urls import url

from . import views

app_name = 'csgo_api'

urlpatterns = [
    url(r'^upcomingMatches/', views.GetUpcomingMatches.as_view()),
    url(r'^matchResult/', views.GetMatchResult.as_view()),
    url(r'^matchResultStats/', views.GetMatchResultStats.as_view()),
]