from django.conf.urls import *
from activitytracker import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^terms_and_conditions/$', views.terms_and_conditions, name='terms_and_conditions'),
    url(r'^social_login/(?P<action>.+)/$', views.social_login, name='social-login'),
    url(r'^account/verification/(?P<verification_token>\w+)/$', views.email_verification, name='emailVerification'),
    url(r'^account/password_reset/(?P<passwordreset_token>\w+)/$', views.password_reset, name='passwordReset'),
    url(r'^account/passforgot/$', views.passwordforget, name='passwordforget'),
    url(r'^account/register/$', views.register, name='register'),

    url(r'^activity/display-activity/(?P<performs_identification>[0-9]+)/$', views.showactivity, name='showactivity'),
    url(r'^activity/delete-activity/(?P<performs_id>[0-9]+)/$', views.deleteactivity, name='deleteactivity'),
    url(r'^activity/edit-activity/(?P<performs_id>[0-9]+)/$', views.editactivity, name='editactivity'),
    url(r'^activity/update-activity/(?P<performs_id>[0-9]+)/$', views.updateactivity, name='updateactivity'),

    url(r'^activity/(?P<performs_id>[0-9]+)/$', views.activitydetails, name='activitydetails'),
    url(r'^settings/$', views.settings_page, name='settings'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^settings/sync/(?P<provider>[-\w]+)/$', views.syncProviderActivities, name='syncProviderActivities'),

]
