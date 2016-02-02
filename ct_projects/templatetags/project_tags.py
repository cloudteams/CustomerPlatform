from django import template
from ct_projects.models import ProjectFollowing

__author__ = 'dipap'

register = template.Library()


@register.filter
def is_followed_by(project, user):
    return ProjectFollowing.objects.filter(project=project, user=user).count() > 0


@register.filter
def count_followers(project):
    return ProjectFollowing.objects.filter(project=project).count()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter
def get_user_rate(idea, user):
    if not user.is_authenticated():
        return None

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


@register.filter
def join(lst, sep):
    return sep.join(lst)


@register.filter
def get_poll_token_link(poll, user):
    return poll.get_poll_token_link(user)


@register.filter
def print_days_left(project):
    days = project.get_days_left()
    if days:
        return str(days)
    else:
        return "-"


@register.filter
def is_liked_by(idea, user):
    if not user.is_authenticated():
        return False

    return idea.ratings.filter(user=user).exists()
