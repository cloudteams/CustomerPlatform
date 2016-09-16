from django.conf.urls import url, include
from gamification import views

__author__ = 'dipap'

urlpatterns = [
    url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),
    url(r'^badge-collection/$', views.badge_collection, name='badge-collection'),
]