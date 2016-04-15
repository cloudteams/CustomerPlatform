from django import template
from ct_projects.models import ProjectFollowing, PollToken
import re

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
    try:
        token = PollToken.objects.get(poll=poll, user=user)
        return token.get_absolute_url()
    except PollToken.DoesNotExist:
        return poll.request_token_link()


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


@register.filter
def get_anonymized_username(item, user):
    return item.get_anonymized_username(user)


@register.filter
def get_keywords(column):
    return [
        ['Business', 'Development', 'Education', 'Entertainment', 'Finance', 'Food & Drink',
         'Games', 'Health & Fitness'],
        ['Lifestyle', 'Medical', 'Music', 'Navigation', 'News', 'Others', 'Photo & Video', 'Productivity'],
        ['Reference', 'Research', 'Social Networking', 'Sports', 'Travel', 'Utilities', 'Weather'],
    ][int(column) - 1]


@register.filter(name='youtube_embed_url')
# converts youtube URL into embed HTML
# value is url
def youtube_embed_url(value):
    matches = re.finditer('(http|https)\:\/\/www\.youtube\.com\/watch\?v\=(\w*)(\&(.*))?', value)
    mv = {}
    for match in matches:
        link = value[match.start():match.end()]
        embed_code = link.split('?v=')[1]
        mv[link] = '<iframe width="560" height="315" src="https://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % embed_code

    for link in mv.keys():
        value = value.replace(link, mv[link])
    return value


@register.filter
def custom_urlize(value):
    matches = re.finditer('www.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)
    mv = {}
    for match in matches:
        link = value[match.start():match.end()]
        if 'youtube.com' in link:
            continue
        mv[link] = '<a target="_blank" href="http://%s">%s</a>' % (link, link)

    for link in mv.keys():
        value = value.replace(link, mv[link])
    return value
