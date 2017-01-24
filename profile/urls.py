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
    url(r'^notifications/(?P<pk>\d+)/perform-main-action/$', views.perform_main_notification_action,
        name='perform-main-notification-action'),
    url(r'^notifications/(?P<pk>\d+)/dismiss/$', views.dismiss_notification, name='notification-dismiss'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^settings/email-notifications/$', views.update_notification_settings, name='update-notification-settings'),
    url(r'^send-invitation/$', views.send_invitation, name='send-invitation'),

    # Send an invitation
    url(r'^password-change/$', views.password_change, name='password-change'),

    # Change password
    url(r'^password-change/$', views.password_change, name='password-change'),

    # Coins
    url(r'^get-current-balance/$', views.get_current_balance, name='password-change'),
]
