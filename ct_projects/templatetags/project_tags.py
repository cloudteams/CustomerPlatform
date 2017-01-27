from django import template
from django.db.models import Q
from django_comments.forms import CommentForm

from ct_projects.models import ProjectFollowing, PollToken, Notification, RewardPurchase, ContactRequest
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
def has_participated_to(user, campaign):
    if not user.is_authenticated():
        return False

    return campaign in user.get_participated_campaigns()


@register.filter
def get_invited_campaigns(project, user):
    if not user.is_authenticated():
        return []

    # find participated campaigns
    campaigns_participated = user.get_participated_campaigns()

    # find invited campaigns
    campaigns_invited = []
    for n in Notification.objects.filter(user=user).filter(Q(document__campaign__project_id=project.pk) |
                                                           Q(poll__campaign__project_id=project.pk)):
        c = n.campaign()
        if c not in campaigns_participated and not c.has_expired():
            campaigns_invited.append(c)

    return list(set(campaigns_invited))


@register.filter
def count_invites_by_project(user, project):
    ns = Notification.objects.filter(user=user).filter(Q(poll__campaign__project_id=project.pk) |
                                                       Q(document__campaign__project_id=project.pk))

    campaigns = []
    for n in ns:
        campaign = n.campaign()

        if not campaign.has_expired():
            campaigns.append(campaign)

    return len(list(set(campaigns)))


@register.filter
def count_rewards_won_by(user, project):
    return RewardPurchase.objects.filter(user=user, reward__project_id=project.pk).count()


@register.filter
def participated_campaigns_number(user, project=None):
    return user.get_participated_campaigns(project=project).count()


@register.filter
def get_comment_form(idea):
    return CommentForm(idea)


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


@register.filter
def has_contacted(user, project):
    return ContactRequest.objects.filter(user_id=user.pk, project_id=project.pk).exists()
