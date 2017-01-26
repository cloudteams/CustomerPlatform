from datetime import date
from django import template
from django.templatetags.static import static

from ct_projects.models import RewardPurchase

__author__ = 'dipap'

register = template.Library()


@register.filter
def get_brand_icon(brand):
    return static('profile/img/brands/%s.png' % brand.lower())


@register.filter
def get_icon_width(brand):
    if brand == 'TWITTER':
        return 40

    return 30


@register.filter
def age_from_birthyear(birthyear):
    return date.today().year - birthyear


@register.filter
def choice_to_str(option, field):
    for o in field._choices:
        if o[0] == option:
            return o[1]

    return option


@register.filter
def to_percent(progress):
    return progress/100.0


@register.filter
def is_profile_incomplete(profile):
    return profile.get_completion_progress() < 50


@register.filter
def nand(a, b):
    return a and not b


@register.filter
def get_year_options(_):
    years = []
    year = date.today().year

    idx = 0
    while idx < 100:
        years.append(year - idx)
        idx += 1

    return years


@register.filter
def get_poll_token_link(poll, user):
    return poll.get_poll_token_link(user)


@register.filter
def was_bought_by(reward, user):
    return RewardPurchase.objects.filter(user_id=user.pk, reward_id=reward.pk).exists()
