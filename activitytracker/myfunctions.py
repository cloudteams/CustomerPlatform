from math import radians, cos, sin, asin, sqrt
import requests
import re
from pygeocoder import Geocoder
from requests_oauthlib import OAuth1
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
import time
from config import *
from django.db import transaction
from AuthorizationChecks import *




def parseYoutubeDurationToTimedelta(time_str):
    """
    This function calculates the timedelta (in seconds) of a Youtube Duration
    format. The main type of format is ISO8601, that is PT#H#M#S or PT#M#S.
    We ignore videos that are greater than 24 hours in duration
    """
    regex = re.compile(r'PT((?P<hours>\d+?)H)?((?P<minutes>\d+?)M)?((?P<seconds>\d+?)S)?')

    parts = regex.match(time_str)

    if not parts:
        return

    parts = parts.groupdict()

    time_params = {}

    for (name, param) in parts.iteritems():

        if param:

            time_params[name] = int(param)

    return timedelta(**time_params)



def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    km = 6367 * c

    return km

def calculateUtcOffset(lat, lng, recorded_datetime):

    if (lat is None) or (lat == 0):
        return 0

    api_url = 'https://maps.googleapis.com/maps/api/timezone/json'
    params = {
        'timestamp': time.mktime(recorded_datetime.timetuple()),
        'location': '%s,%s' % (str(lat), str(lng))
    }

    r = requests.get(url=api_url, params=params).json()

    if r['status'] != 'OK':
        return 0

    return (r['rawOffset'] + r['dstOffset']) / 3600



def addActivityFromProvider(user, goal, goal_status, friends, objects, result, location_lat, location_lng,
                            location_address, start_date, end_date, activity, utc_offset=0):

    """
    Create an Activity Object from the data provided in the parameters.
    Also, add any new objects or friends to the objects and friend lists of
    the current user
    """
    performs_instance = Performs(user=user,
                                 activity=activity,
                                 friends=friends,
                                 goal=goal,
                                 goal_status=goal_status,
                                 location_address=location_address,
                                 location_lat=location_lat,
                                 location_lng=location_lng,
                                 start_date=start_date,
                                 end_date=end_date,
                                 result=result,
                                 utc_offset=utc_offset
    )

    performs_instance.save()

    for friend_name in friends.split(','):

        friend = friend_name.lstrip(' ')
        if user.friend_set.filter(friend_name=friend).count() == 0 and friend:

            instance = Friend(friend_name=friend, friend_of_user=user)
            instance.save()

    for tool_name in objects.split(','):

        tool = tool_name.lstrip(' ')
        if user.object_set.filter(object_name=tool).count() == 0 and tool:

            object_instance = Object(object_name=tool, object_of_user=user)
            object_instance.save()

        elif tool:
            object_instance = user.object_set.get(object_name=tool)

        else:
            continue

        performs_instance.using.add(object_instance)

    return performs_instance



def createActivityLinks(provider, instance, provider_instance_id, url):

    """
    Create a link between the Activity object in Activity Tracker and its
    corresponding in the provider database
    """
    link_instance = PerformsProviderInfo(provider=provider,
                                         instance=instance,
                                         provider_instance_id=str(provider_instance_id),
                                         provider_instance_url=url
    )

    link_instance.save()

    return 'Done'



def placesNearActivity(user, activity, place, radius):

    places_returned_list = []
    if place == "all":
        all_places = [p for p in user.places_set.all()]
        for p in all_places:
            if haversine(p.place_lat,p.place_lng, activity.location_lat, activity.location_lng) <= float(radius):
                places_returned_list.append(p.place_name)
    elif place == "Everywhere else":
        all_places = [p for p in user.places_set.all()]
        for p in all_places:
            if haversine(p.place_lat,p.place_lng, activity.location_lat, activity.location_lng) <= float(radius):
                return []

        places_returned_list.append("Everywhere else")
    else:
        place_object = user.places_set.get(place_name=place)
        if haversine(place_object.place_lat, place_object.place_lng, activity.location_lat, activity.location_lng) <= float(radius):
            places_returned_list.append(place_object.place_name)
    return places_returned_list


def assignDurationInterval(duration):
    if duration.days > 0:
        return "> 24"

    if duration.seconds > 36000:
        return "10-24"
    elif duration.seconds > 18000:
        return "5-10"
    elif duration.seconds > 7200:
        return "2-5"
    elif duration.seconds > 3600:
        return "1-2"
    elif duration.seconds > 1800:
        return "0.5-1"
    else:
        return "0-0.5"


def getAppManagementDomValues(status, provider):
    if status == "Not Connected":
        return {
            'buttonIcon': 'circle-arrow-right',
            'buttonText': 'Connect',
            'statusText': 'App not Connected',
            'statusIcon': 'icon-remove-circle',
            'statusFontColor': 'red',
            'providerIconName': provider
        }
    elif status == "Authentication Failed":
        return {
            'buttonIcon': 'repeat',
            'buttonText': 'Re-Authorize',
            'statusText': 'Expired or de-authorized',
            'statusIcon': 'icon-warning-sign',
            'statusFontColor': 'orangered',
            'providerIconName': provider
        }
    elif status == "Cannot Process Request":
        return {
            'buttonIcon': 'repeat',
            'buttonText': 'Retry',
            'statusText': 'Too many requests sent. Try again later',
            'statusIcon': 'icon-warning-sign',
            'statusFontColor': 'red',
            'providerIconName': provider
        }
    else:
        return {
            'buttonIcon': 'trash',
            'buttonText': 'De-Authorize',
            'statusText': 'App connected',
            'statusIcon': 'icon-ok-circle',
            'statusFontColor': 'green',
            'providerIconName': provider
        }


# Returns a list of the names of the user's personal routine activities
def getRoutineList(user, shared_routine_list):

    user_extra_routines = user.routine_set.exclude(
        activity__activity_name__in=shared_routine_list
    ).values_list('activity__activity_name', flat=True)

    return shared_routine_list + list(user_extra_routines)


# Returns the data of the routines in a formatted way, to present them in settings
def getFormattedRoutines(user, shared_routine_list, day_types):

    user_routines_all = getRoutineList(user, shared_routine_list)

    basicRoutineActivities = dict()
    for activity_name in user_routines_all:

        activity = Activity.objects.get(activity_name=activity_name)
        basicRoutineActivities[activity.activity_name] = {
            'color': activity.category,
            'icon_classname': activity.icon_classname,
        }

        for day_type in day_types:

            if day_type not in basicRoutineActivities[activity.activity_name]:
                basicRoutineActivities[activity.activity_name][day_type] = list()

            routine_data_logs = user.routine_set.filter(activity=activity, day_type=day_type)
            if not routine_data_logs:
                (basicRoutineActivities[activity.activity_name][day_type]).append({
                    'time': ' - ',
                    'season': ''
                })
                continue

            for routine_data_log in routine_data_logs:

                start_time = '' if not routine_data_log.start_time else routine_data_log.start_time.strftime('%H:%M')
                end_time = '' if not routine_data_log.end_time else routine_data_log.end_time.strftime('%H:%M')

                seasonality_start = '' if not routine_data_log.seasonal_start else routine_data_log.seasonal_start.strftime('%m/%d')
                seasonality_end = '' if not routine_data_log.seasonal_end else routine_data_log.seasonal_end.strftime('%m/%d')

                if not seasonality_start:
                    (basicRoutineActivities[activity.activity_name][day_type]).append({
                        'time': '%s - %s' % (start_time, end_time),
                        'season': 'All Year'
                    })
                else:
                    (basicRoutineActivities[activity.activity_name][day_type]).append({
                        'time': '%s - %s' % (start_time, end_time),
                        'season': '%s - %s' % (seasonality_start, seasonality_end)
                    })
    print basicRoutineActivities
    return basicRoutineActivities
