from datetime import date
from django import template

__author__ = 'dipap'

register = template.Library()


@register.filter
def age_from_birthyear(birthyear):
    return date.today().year - birthyear


@register.filter
def choice_to_str(option, field):
    for o in field._choices:
        if o[0] == option:
            return o[1]

    return option
