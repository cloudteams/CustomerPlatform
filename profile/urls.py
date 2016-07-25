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

    # Notification
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^notification/(?P<pk>\d+)/$', views.notification_view, name='notification-view'),

    # Change password
    url(r'^password-change/$', views.password_change, name='password-change'),
]
