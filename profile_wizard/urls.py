from django.conf.urls import url, include
from profile_wizard import views

__author__ = 'dipap'

urlpatterns = [
    # start the wizard
    url(r'^$', views.start_wizard, name='start-profile-wizard'),
]
