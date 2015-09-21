from django import template
from ct_projects.models import ProjectFollowing

__author__ = 'dipap'

register = template.Library()


@register.filter
def is_followed_by(project, user):
    return ProjectFollowing.objects.filter(project_pk=project.pk, user=user).count() > 0


@register.filter
def count_followers(project):
    return ProjectFollowing.objects.filter(project_pk=project.pk).count()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()