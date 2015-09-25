from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^activitytracker/', include('activitytracker.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),

    # projects
    url(r'^projects/', include('ct_projects.urls')),

    # home page redirect
    url(r'^$', RedirectView.as_view(url='activitytracker/', permanent=True)),
]
