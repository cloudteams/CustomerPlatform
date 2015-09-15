from django.conf.urls import url
from ct_projects import views

__author__ = 'dipap'

urlpatterns = [
    # projects home
    url(r'^$', views.list_projects, name='all-projects'),

    # following projects
    url(r'^(?P<pk>[\w-]+)/follow/$', views.follow_project, name='follow-project'),
    url(r'^(?P<pk>[\w-]+)/unfollow/$', views.unfollow_project, name='unfollow-project')
]
