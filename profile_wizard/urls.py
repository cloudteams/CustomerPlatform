from django.conf.urls import url, include
from profile_wizard import views

__author__ = 'dipap'

urlpatterns = [
    # start the wizard
    url(r'^$', views.start_wizard, name='start-profile-wizard'),

    # Brand opinions
    url(r'^get-brand-opinion$', views.get_brand_opinion, name='get-brand-opinion'),
    url(r'^opinion-about$', views.opinion_about, name='opinion-about'),
]
