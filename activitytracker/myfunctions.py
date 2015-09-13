from math import radians, cos, sin, asin, sqrt
import requests
import re
from pygeocoder import Geocoder
from requests_oauthlib import OAuth1
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
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


def addActivityFromProvider(user, goal, goal_status, friends, objects, result, location_lat, location_lng,
                            location_address, start_date, end_date, activity):

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
                                 result=result
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
        return {     'buttonText': 'Connect App',
                     'buttonClassColor': 'blueNavy',
                     'statusText': 'App not Connected',
                     'statusIcon': 'icon-remove-circle',
                     'statusFontColor': 'red',
                     'providerIconName': provider
        }
    elif status == "Authentication Failed":
        return {     'buttonText': 'Re-authorize',
                     'buttonClassColor': 'orange',
                     'statusText': 'App manually de-authorized or token expired',
                     'statusIcon': 'icon-warning-sign',
                     'statusFontColor': 'orange',
                     'providerIconName': provider
        }
    elif status == "Cannot Process Request":
        return {     'buttonText': 'Try again',
                     'buttonClassColor': '#850521 ',
                     'statusText': 'Too many requests sent. Try again later',
                     'statusIcon': 'icon-warning-sign',
                     'statusFontColor': 'red',
                     'providerIconName': provider
        }
    else:
        return {     'buttonText': 'Disconnect',
                     'buttonClassColor': 'red',
                     'statusText': 'App connected',
                     'statusIcon': 'icon-ok-circle',
                     'statusFontColor': 'green',
                     'providerIconName': provider
        }



