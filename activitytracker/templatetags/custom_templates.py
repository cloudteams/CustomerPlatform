from django import template
from datetime import datetime
from django.core.serializers import serialize
import json
from django.db.models.query import QuerySet
from activitytracker.models import *

register = template.Library()


@register.filter
def my_replace(value):  # Only one argument.
    # Replaces ' with "
    tostring = '", "'.join(value)
    return '["' + tostring + '"]'


@register.filter
def dividable_by_six(value):
    # Performs a div operation
    return value % 6 == 0


@register.filter
def divide_with_6(value):
    # Performs a div operation
        return value / 6

@register.filter
def grouped_duration(value):
    duration = datetime.now() - datetime.now()
    for entry in value:
        duration += entry.end_date - entry.start_date
    days, seconds = duration.days, duration.seconds
    hours = seconds/3600
    minutes = (seconds - hours*3600)/60
    a = [days, hours, minutes]
    if a[0] == 0:
            if a[1] == 0:
                return "%sm" % a[2]
            else:
                if a[2] == 0:
                    return "%sh" % a[1]
                else:
                    return "%sh%sm" % (a[1], a[2])
    else:
            if a[1] == 0:
                if a[2] == 0:
                    return "%sd" % a[0]
                else:
                    return "%sd%sm" % (a[0], a[2])
            else:
                if a[2] == 0:
                    return "%sd%sh" % (a[0], a[1])
                else:
                    return "%sd%sh%sm" % (a[0], a[1], a[2])


@register.filter
def grouped_id(value):
    id_list=[]
    for entry in value:
        id_list.append(entry.id)
    return '_'.join(str(an_id) for an_id in id_list)



@register.filter
def remove_spaces(value):
    parts = value.split(" ")
    return "".join(str(p) for p in parts)

@register.filter
def is_false(arg):
    return arg is False

@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return json.dumps(object)


@register.filter
def capitalizeFirstLetter(value):
    return value.title()


@register.filter
def addSpaceAfterComma(value):
    parts = value.split(',')
    return ', '.join(parts)

@register.filter
def removeDashes(value):
    return value.replace('-', ' ')

@register.filter
def addDashes(value):
    return value.replace(' ', '-')

@register.filter
def shorten(a):
    if len(a) > 20:
        return a.split('/')[1]
    return a
