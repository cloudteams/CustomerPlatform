from datetime import date
from django import template
from django.templatetags.static import static

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
