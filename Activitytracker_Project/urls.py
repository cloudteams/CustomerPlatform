import os

from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

import ct_projects

handler404 = 'ct_projects.views.handler_404'

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^activitytracker/', include('activitytracker.urls')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),

    # projects
    url(r'^projects/', include('ct_projects.urls')),

    # user profile wizard
    url(r'^profile/', include('profile.urls')),

    # gamification
    url(r'^gamification/', include('gamification.urls')),

    # terms & conditions and privacy policy
    url(r'^terms-and-conditions/$', ct_projects.views.terms_and_conditions, name='terms-and-conditions'),
    url(r'^privacy-policy/$', ct_projects.views.privacy_policy, name='privacy-policy'),

    # home page redirect
    url(r'^$', RedirectView.as_view(url='projects/', permanent=True)),

    # developer registration cookie redirect page
    url(r'^developer/account/register', ct_projects.views.developer_registration),

    # media URL
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
