from django.conf.urls import url
from ct_projects import views

__author__ = 'dipap'

urlpatterns = [
    url(r'^$', views.list_projects, name='all-projects'),

    
]
