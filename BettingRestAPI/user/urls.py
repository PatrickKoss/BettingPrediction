from django.conf.urls import url

from . import views

app_name = 'user'

urlpatterns = [
    url(r'^login/', views.Login.as_view()),
    url(r'^logout/', views.Logout.as_view()),
    url(r'^authenticated/', views.GetAuthenticated.as_view()),
    url(r'^register/', views.Register.as_view()),
    url(r'^delete/(?P<id>[0-9]+)$', views.DeleteUser.as_view(), name='id'),
    url(r'^update/', views.UpdateUser.as_view()),
]
