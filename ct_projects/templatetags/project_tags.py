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


@register.filter
def get_user_rate(idea, user):
    qs = idea.ratings.filter(user=user)
    if qs:
        return qs[0]
    else:
        return None


@register.filter
def rate_larger_than(rating, i):
    if not rating:
        return False

    return rating >= int(i)
