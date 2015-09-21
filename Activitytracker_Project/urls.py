from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^activitytracker/', include('activitytracker.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^projects/', include('ct_projects.urls')),
]
