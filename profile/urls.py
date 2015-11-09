from django.conf.urls import url, include
from profile import views

__author__ = 'dipap'

urlpatterns = [
    # profile
    url(r'^$', views.view_my_profile, name='view-my-profile'),
    url(r'^edit/$', views.start_wizard, name='start-profile-wizard'),

    # Brand opinions
    url(r'^get-brand-opinion$', views.get_brand_opinion, name='get-brand-opinion'),
    url(r'^opinion-about$', views.opinion_about, name='opinion-about'),
]
