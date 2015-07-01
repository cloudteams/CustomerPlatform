from math import radians, cos, sin, asin, sqrt
import requests
from social.apps.django_app.default.models import *
from activitytracker.models import *
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from pygeocoder import Geocoder


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


def providerData(provider, access_token):
    url_headers_dict = {
        'runkeeper': {
                    'headers':{
                         'Host': 'api.runkeeper.com',
                         'Authorization': 'Bearer '+ str(access_token),
                         'Accept': 'application/vnd.com.runkeeper.User+json'
                     },
                    'url': 'http://api.runkeeper.com/user'
        }
    }
    return url_headers_dict[provider]


def syncRunkeeperActivities(user):

    # function that will fetch us the ids based on the url and headers we provided. Returns the list passed + the new ids
    def fetchRunkeeperFitnessActivityIds(passed_url, passed_headers):
        list_of_ids = []
        next_page_exists = True
        current_url = passed_url
        current_headers = passed_headers
        while next_page_exists:
            r = requests.get(current_url, headers=current_headers)
            # If activities were returned OR activities have been modified (we need it only on the 1st iteration)
            if r.status_code != 304:
                try:
                    # try removing this header but only if it was present.
                    current_headers.pop("If-Modified-Since")
                    # If it wasn't just 'pass'
                except KeyError:
                    pass

                rest_response_json = r.json()
                if not rest_response_json['items']:
                    return []
                for activity in rest_response_json['items']:
                    list_of_ids.append(activity['uri'].split("/fitnessActivities/")[1])
                    try:
                        current_url = 'http://api.runkeeper.com' + rest_response_json['next']
                    except KeyError:
                        next_page_exists = False
            else:
                # if status = 304 that means that we had an 'if-modified' check and nothing was modified
                # so we force the iteration to stop
                return []

        return list_of_ids
    # End of Function 1 ------------------ Start of function 2

    # function that will get the detailed info for each activity and put them into the database
    def insertRunkeeperFitnessActivities(token, id_list):
        url = 'http://api.runkeeper.com/fitnessActivities/'
        headers = {  'Host': 'api.runkeeper.com',
                     'Authorization': 'Bearer ' + str(token),
                     'Accept': 'application/vnd.com.runkeeper.FitnessActivity+json',
        }

        for runkeeper_id in id_list:
            current_url = url + str(runkeeper_id)
            # fetch details of activity
            r = requests.get(current_url, headers=headers).json()
            activity = Activity.objects.get(activity_name=r['type'])
            start_date = datetime.strptime(r['start_time'],'%a, %d %b %Y %H:%M:%S')
            end_date = start_date + timedelta(seconds=r['duration'])
            object = r['equipment']
            result = ''
            try:
                distance = str(int(round(r['total_distance'])))
                result += 'Covered ' + distance + ' Metres. '
            except KeyError:
                pass
            try:
                calories = str(int(round(r['total_calories'])))
                result += 'Burned ' + calories + ' Calories.'
            except KeyError:
                pass
            try:
                location_lat = float(r['path'][0]['latitude'])
                location_lng = float(r['path'][0]['longitude'])
                location_address = str(Geocoder.reverse_geocode(r['path'][0]['latitude'],r['path'][0]['longitude'])[0])
            except:
                location_lat = None
                location_lng = None
                location_address = ""

            # if object != none and it's not registered under the user, register it
            if user.object_set.filter(object_name=object).count() == 0 and object != "None":
                a = Object(object_name=object, object_of_user=user)
                a.save()

            # if activity already existed
            if PerformsProviderInfo.objects.filter(provider='runkeeper', provider_instance_id=str(runkeeper_id)).count() > 0:
                p = PerformsProviderInfo.objects.get(provider='runkeeper', provider_instance_id=str(runkeeper_id))
                performs_instance = p.instance
                performs_instance.activity = activity
                performs_instance.start_date = start_date
                performs_instance.end_date = end_date
                performs_instance.location_lat = location_lat
                performs_instance.location_lng = location_lng
                performs_instance.location_address = location_address
                performs_instance.result = result
                performs_instance.save()
                if object == "None":
                    continue
                object_object = user.object_set.get(object_name=object)
                if len(performs_instance.using.all()) == 1 and performs_instance.using.all()[0] in ["readmill", "Stationary Bike", "Elliptical", "Row Machine"]:
                    performs_instance.using.remove()
                    performs_instance.using.add(object_object)
                else:
                    performs_instance.using.add(object_object)
                performs_instance.save()
            # if activity didnt exist, we need to create an instance
            else:
                performs_instance = Performs(user=user, activity=activity, friends='', goal='', goal_status=None,
                                             location_address=location_address, location_lat=location_lat,
                                             location_lng=location_lng, start_date=start_date, end_date=end_date,
                                             result=result)
                performs_instance.save()
                if object != "None":
                    object_object = user.object_set.get(object_name=object)
                    performs_instance.using.add(object_object)
                    performs_instance.save()
                p = PerformsProviderInfo(provider='runkeeper', instance=performs_instance, provider_instance_id=str(runkeeper_id))
                p.save()

        return
    # End of Function 2 ----------------------------- Start of function for sleep activities

    def fetchAndInsertRunkeeperSleepActivities(passed_url, passed_headers):
        next_page_exists = True
        current_url = passed_url
        current_headers = passed_headers
        while next_page_exists:
            r = requests.get(current_url, headers=current_headers)
            # If activities were returned OR activities have been modified (we need it only on the 1st iteration)
            if r.status_code != 304:
                try:
                    # try removing this header but only if it was present.
                    current_headers.pop("If-Modified-Since")
                    # If it wasn't just 'pass'
                except KeyError:
                    pass

                rest_response_json = r.json()
                if not rest_response_json['items']:
                    return 0
                for activity in rest_response_json['items']:
                    runkeeper_id = activity['uri'].split("/sleep/")[1]
                    activity_name = Activity.objects.get(activity_name="Sleeping")
                    start_date = datetime.strptime(activity['timestamp'],'%a, %d %b %Y %H:%M:%S')
                    end_date = start_date + timedelta(seconds=activity['total_sleep']*60)
                    hours_of_sleep = activity['total_sleep']/60
                    if hours_of_sleep <= 4.0:
                        result = "Got only a bit of energy back"
                    elif hours_of_sleep <= 6.5:
                        result = "Rested, but not fully"
                    else:
                        result = "Had an almost perfectly fulfilling sleep"


                    # if activity already existed
                    if PerformsProviderInfo.objects.filter(provider='runkeeper', provider_instance_id=str(runkeeper_id)).count() > 0:
                        p = PerformsProviderInfo.objects.get(provider='runkeeper', provider_instance_id=str(runkeeper_id))
                        performs_instance = p.instance
                        # The only editable thing is the duration. So we only change that
                        performs_instance.end_date = end_date
                        performs_instance.result = result
                        performs_instance.save()
                    # if activity didnt exist, we need to create an instance
                    else:
                        performs_instance = Performs(user=user, activity=activity_name, friends='', goal='', goal_status=None,
                                                     location_address="", location_lat=None, location_lng=None,
                                                     start_date=start_date, end_date=end_date, result=result)
                        performs_instance.save()
                        try:
                            a = user.object_set.get(object_name='RunKeeper')
                        except ObjectDoesNotExist:
                            a = Object(object_name='RunKeeper', object_of_user=user)
                            a.save()
                        performs_instance.using.add(a)
                        performs_instance.save()
                        p = PerformsProviderInfo(provider='runkeeper', instance=performs_instance, provider_instance_id=str(runkeeper_id))
                        p.save()

                    try:
                        current_url = 'http://api.runkeeper.com' + rest_response_json['next']
                    except KeyError:
                        next_page_exists = False
            else:
                # if status = 304 that means that we had an 'if-modified' check and nothing was modified
                # so we force the iteration to stop
                return 0

        return 1


    # main
    social_auth_instance = user.social_auth.get(provider='runkeeper')
    access_token = social_auth_instance.extra_data['access_token']
    url = 'http://api.runkeeper.com/fitnessActivities'
    headers = {  'Host': 'api.runkeeper.com',
                 'Authorization': 'Bearer '+ str(access_token),
                 'Accept': 'application/vnd.com.runkeeper.FitnessActivityFeed+json',
    }

    # If it's not the first time we are syncing activities. We get the new activities that have happened after our last
    # call + any old activity that has been modified after out last call.
    try:
        last_updated = social_auth_instance.extra_data['last_updated']
        partition_barrier = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        # we get the activities that were modified after the time of the last sync. The previous changes are already migrated
        last_updated_url_for_activities = url + '?modifiedNoEarlierThan=' + partition_barrier
        last_updated_headers_for_activities = headers.copy()
        last_updated_headers_for_activities['If-Modified-Since'] = datetime.strptime(last_updated,"%Y-%m-%d %H:%M:%S").strftime('%a, %d %b %Y %H:%M:%S GMT')
        runkeeper_activity_id_list = fetchRunkeeperFitnessActivityIds(last_updated_url_for_activities, last_updated_headers_for_activities)
    # Field "last_updated" is not present. Thus we will ask for all the activities
    except KeyError:
        runkeeper_activity_id_list = fetchRunkeeperFitnessActivityIds(url, headers)
    print runkeeper_activity_id_list
    insertRunkeeperFitnessActivities(access_token, runkeeper_activity_id_list)

    # End for Fitness Activities, start of sleep activities
    url = 'http://api.runkeeper.com/sleep'
    headers = {  'Host': 'api.runkeeper.com',
                 'Authorization': 'Bearer '+ str(access_token),
                 'Accept': 'application/vnd.com.runkeeper.SleepSetFeed+json',
    }
    try:
        last_updated = social_auth_instance.extra_data['last_updated']
        partition_barrier = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        # we get the activities that were modified after the time of the last sync. The previous changes are already migrated
        last_updated_url_for_activities = url + '?modifiedNoEarlierThan=' + partition_barrier
        last_updated_headers_for_activities = headers.copy()
        last_updated_headers_for_activities['If-Modified-Since'] = datetime.strptime(last_updated,"%Y-%m-%d %H:%M:%S").strftime('%a, %d %b %Y %H:%M:%S GMT')
        sleep_activity_number = fetchAndInsertRunkeeperSleepActivities(last_updated_url_for_activities, last_updated_headers_for_activities)
    # Field "last_updated" is not present. Thus we will ask for all the activities
    except KeyError:
        sleep_activity_number = fetchAndInsertRunkeeperSleepActivities(url, headers)


    social = user.social_auth.get(provider='runkeeper')
    social.extra_data['last_updated'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    social.save()

    if (not runkeeper_activity_id_list) and  sleep_activity_number == 0:
        return HttpResponseBadRequest('Runkeeper Activities are already up to date')
    else:
        return HttpResponse('Runkeeper Activities have been synced')








def checkConnection(user, provider):
    try:
        social = user.social_auth.get(provider=provider)
        access_token = social.extra_data['access_token']
    except ObjectDoesNotExist:
        return 'Not Connected'
    provider_data = providerData('runkeeper', str(access_token))
    r = requests.get(provider_data['url'], headers=provider_data['headers']).json()
    try:
        if r['reason'] == "Revoked":
            return 'Authentication Failed'
    except KeyError:
        pass
    return 'Authentication Successful'


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
                     'statusText': 'App manually de-authorized',
                     'statusIcon': 'icon-warning-sign',
                     'statusFontColor': 'orange',
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


# only providers that cant supply our app with activity data. Not providers for simply logging in
available_providers = ['runkeeper']
providerSyncFunctions = {
        'runkeeper': syncRunkeeperActivities,
        #'facebook': syncFacebookActivities,
        #'google': syncGoogleActivities
    }
