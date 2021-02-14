from django.conf.urls import url

from . import views

app_name = 'user'

urlpatterns = [
    url(r'^login/', views.Login.as_view()),
    url(r'^logout/', views.Logout.as_view()),
    url(r'^authenticated/', views.GetAuthenticated.as_view()),
    url(r'^(?P<id>[0-9]+)$', views.UsersModification.as_view()),
    url('', views.Users.as_view()),
]
