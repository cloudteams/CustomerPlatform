from django.conf.urls import url
from ct_projects import views

__author__ = 'dipap'

urlpatterns = [
    # projects lists
    url(r'^$', views.list_projects, name='all-projects'),
    url(r'^followed-projects/$', views.followed_projects, name='followed-projects'),

    # project details
    url(r'^(?P<pk>[\w-]+)/$', views.project_details, name='project-details'),

    # following projects
    url(r'^(?P<pk>[\w-]+)/follow/$', views.follow_project, name='follow-project'),
    url(r'^(?P<pk>[\w-]+)/unfollow/$', views.unfollow_project, name='unfollow-project')
]
