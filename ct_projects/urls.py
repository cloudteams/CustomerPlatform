from django.conf.urls import url, include
from ct_projects import views, project_api

__author__ = 'dipap'

urlpatterns = [
    # projects lists
    url(r'^$', views.list_projects, name='all-projects'),
    url(r'^followed/$', views.followed_projects, name='followed-projects'),
    url(r'^followed/campaigns$', views.followed_campaigns, name='followed-campaigns'),

    # ideas
    url(r'^(?P<pk>[\w-]+)/post-idea/$', views.post_idea, name='post-idea'),
    url(r'^(?P<project_pk>[\w-]+)/ideas/(?P<pk>\d+)$', views.idea_details, name='idea-details'),
    url(r'^(?P<project_pk>[\w-]+)/ideas/(?P<pk>\d+)/rate/$', views.rate_idea, name='rate-idea'),

    # project details
    url(r'^(?P<pk>\d+)/$', views.project_details, name='project-details'),

    # following projects
    url(r'^(?P<pk>\d+)/follow/$', views.follow_project, name='follow-project'),
    url(r'^(?P<pk>\d+)/unfollow/$', views.unfollow_project, name='unfollow-project'),

    # comments
    url(r'^comments/posted/$', views.comment_posted),
    url(r'^comments/', include('django_comments.urls')),

    # campaigns, polls & documents
    url(r'^(?P<project_pk>[\w-]+)/campaigns/(?P<pk>\d+)$', views.campaign_details, name='campaign-details'),
    url(r'^(?P<project_pk>[\w-]+)/polls/(?P<pk>\d+)/token/$', views.request_poll_token, name='request-poll-token'),

    # generic
    url(r'^how-it-works$', views.how_it_works, name='how-it-works'),

    # project API
    url(r'^api/all/$', project_api.project_list),
    url(r'^api/(?P<pk>\d+)/$', project_api.project),
    url(r'^api/tokens/(?P<nonce>[\w-]+)/mark-as-used/$', project_api.update_poll_token),
    url(r'^api/tokens/(?P<nonce>[\w-]+)/mark-as-completed/$', project_api.mark_token_as_completed),
    url(r'^api/(?P<pk>\d+)/notify-users/$', project_api.notify_users),
]
