from math import radians, cos, sin, asin, sqrt
import requests
import re
from social.apps.django_app.default.models import *
from activitytracker.models import *
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from pygeocoder import Geocoder
from config import *
from tweetpony import APIError
import tweetpony
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import httplib2
from oauth2client.client import AccessTokenCredentials, AccessTokenCredentialsError
from googleapiclient.discovery import build

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

    performs_instance = Performs(user=user, activity=activity, friends=friends, goal=goal, goal_status=goal_status,
             location_address=location_address, location_lat=location_lat, location_lng=location_lng,
             start_date=start_date, end_date=end_date, result=result)
    performs_instance.save()

    for friend in friends.split(','):
        try:
            user.friend_set.get(friend_name=friend)
        except ObjectDoesNotExist:
            if not friend:
                continue
            instance = Friend(friend_name=friend, friend_of_user=user)
            instance.save()

    for tool in objects.split(','):
        try:
            object_instance = user.object_set.get(object_name=tool)
        except ObjectDoesNotExist:
            if not tool:
                continue
            object_instance = Object(object_name=tool, object_of_user=user)
            object_instance.save()
        performs_instance.using.add(object_instance)

    return performs_instance


def createActivityLinks(provider, instance, provider_instance_id, url ):
    if createActivityLinks:
        link_instance = PerformsProviderInfo(provider=provider, instance=instance,
                                             provider_instance_id=str(provider_instance_id), provider_instance_url=url)
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
                location_lat = location_lng = None
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

                createActivityLinks('runkeeper', performs_instance, str(runkeeper_id), r['activity'] )

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


def syncTwitterActivities(user):
    social_auth_instance = user.social_auth.get(provider='twitter')
    twitter_user_id = social_auth_instance.extra_data['id']
    try:
        api = tweetpony.API(consumer_key=SOCIAL_AUTH_TWITTER_KEY,
                            consumer_secret=SOCIAL_AUTH_TWITTER_SECRET,
                            access_token_secret=str(social_auth_instance.extra_data['access_token']['oauth_token_secret']),
                            access_token=str(social_auth_instance.extra_data['access_token']['oauth_token'])
        )
    except APIError:
        return HttpResponse('Too many requests. Please try again in a few minutes')

    while True:
        try:
            # I am breaking the Calls so that im only asking for old OR new tweets. If i asked for both i would waste
            # the 15 calls/15 minutes that twitter provides me. This way i can get more data inside the 15min window

            since_id = social_auth_instance.extra_data['since_id']
            max_id = social_auth_instance.extra_data['max_id']
            read_all_past_tweets = social_auth_instance.extra_data['read_all_past_tweets']

            # If i haven't read all the past tweets i'll ask only for old tweets until i get them all
            if not read_all_past_tweets:
                tweets= api.user_timeline(user_id=twitter_user_id, count=200, trim_user=True, include_rts=True,
                                       exclude_replies=True, max_id=max_id, contributor_details=True)
                if not tweets:
                    read_all_past_tweets = social_auth_instance.extra_data['read_all_past_tweets'] = True

            # If i have finished with the old, i can ask only for new tweets that happen after the last sync
            if read_all_past_tweets:
                tweets = api.user_timeline(user_id=twitter_user_id, count=200, trim_user=True, include_rts=True,
                                       exclude_replies=True, since_id=since_id, contributor_details=True)

        # Exception happens if i haven't synced before
        except KeyError:
            tweets = api.user_timeline(user_id=twitter_user_id, count=200, trim_user=False, include_rts=True,
                                       exclude_replies=True, contributor_details=True)
            max_id = since_id = 0
            social_auth_instance.extra_data['read_all_past_tweets'] = False

        # If set is Empty i'm done syncing
        if not tweets:
            social_auth_instance.save()
            break

        # If max API Calls for the time window is reached, tweets variable will contain a field 'errors'
        try:
            tweets[0]['errors']
            return HttpResponseBadRequest('Request Limit Reached. Please Re-Sync in a few minutes time')
        except:
            pass

        for tweet in tweets:

            # Get type of tweet, simple or retweet and choose the proper "result" text
            if tweet.retweeted:
                activity_performed = Activity.objects.get(activity_name="Share / Retweet")
                result = "Including yours, there is a total of " + str(tweet.retweet_count) + " retweets at the moment."
                if tweet.favorited:
                    result = "You have favorited this tweet. " + result
            else:
                activity_performed = Activity.objects.get(activity_name="Status Update")
                result = "Your tweet has been retweeted " + str(tweet.retweet_count) + " and favorited " + \
                         str(tweet.favorite_count) + " times at the moment"

            # Check if the user has picked the "Exact Location" Option
            if tweet.coordinates is not None:
                location_lat = tweet.coordinates['coordinates'][1]
                location_lng = tweet.coordinates['coordinates'][0]
                location_address = str(Geocoder.reverse_geocode(location_lat, location_lng)[0])
            # Else if check if the user has chosen the simple "Location" Option
            elif tweet.place is not None:
                location_lat = (tweet.place['bounding_box']['coordinates'][0][0][1] \
                               + tweet.place['bounding_box']['coordinates'][0][2][1]) /2.0
                location_lng = (tweet.place['bounding_box']['coordinates'][0][0][0] \
                               + tweet.place['bounding_box']['coordinates'][0][1][0]) /2.0
                location_address = tweet.place['full_name']
            # Else, if there was no Location added
            else:
                location_lat = location_lng = None
                location_address = ""

            # The medium used for the status update. Here is Twitter but elsewhere could be others i.e. Facebook
            object_used = "Twitter"

            # We cant access the Goal of the user from Twitter
            goal = ""
            goal_status = None

            # The starting time of the tweet is standardized as 1 min before the tweet was posted
            start_date = datetime.strptime(str(tweet.created_at), "%Y-%m-%d %H:%M:%S") - timedelta(seconds=60)
            end_date = datetime.strptime(str(tweet.created_at), "%Y-%m-%d %H:%M:%S")

            # The physical entities that participated in the tweet
            # If it exists, remove the user from the list of friends (since he might have tagged himself)
            friends_list = (list(set([user_mention['name'] for user_mention in tweet.entities['user_mentions']])))
            try:
                friends_list.remove(tweet.user.name)
            except ValueError:
                pass

            # The friends that participated in the Activity
            friends = ','.join(friends_list)

            # Add the activity to the database
            performs_instance = addActivityFromProvider(user=user, activity=activity_performed, friends=friends,
                                    goal=goal, goal_status=goal_status, location_address=location_address,
                                    location_lat=location_lat, location_lng=location_lng, start_date=start_date,
                                    end_date=end_date, result=result, objects=object_used)

            # Update max_id (will help to get tweets older than the id of this tweet) for optimization of results
            if (tweet.id < max_id) or (max_id == 0):
                max_id = tweet.id

            # Update since_id (will help to get tweets more recent than this tweet) for optimization of results
            if (tweet.id > since_id) or (since_id == 0):
                since_id = tweet.id

            # Store the activity "linking" in our database
            tweet_url = "https://twitter.com/statuses/" + tweet.id_str
            createActivityLinks('twitter', performs_instance, str(tweet.id), tweet_url)

        # reduce by 1 so we don't fetch the same tweet again
        if max_id != 0:
            max_id -= 1

        # Store user variables inside the database
        social_auth_instance.extra_data['max_id'] = max_id
        social_auth_instance.extra_data['since_id'] = since_id

        # Save everything
        social_auth_instance.save()

    return HttpResponse("Twitter Activities have been synced")


def syncInstagramActivities(user):
    social_auth_instance = user.social_auth.get(provider='instagram')
    user_instagram_id = social_auth_instance.uid

    # Fetch InstagramUser instance and check if call limit exceeded or if user de-authenticated while the Activity
    # Tracker page hasn't been refreshed and updated
    try:
        api = InstagramAPI(access_token=social_auth_instance.extra_data['access_token'],
                           client_secret=SOCIAL_AUTH_INSTAGRAM_SECRET)
    except InstagramAPIError as error:
        if error.status_code in (420, 429):
            return HttpResponse('Too many requests. Please try again in a few minutes')
        else:
            return HttpResponseBadRequest('Authentication Error. Please refresh the page and re-authorize')

    # If another sync has already taken place for the user
    try:
        since_id = social_auth_instance.extra_data['since_id']
        feed, next_url = api.user_recent_media(user_id=user_instagram_id, min_id=since_id)
        if not feed:
            return HttpResponse("Instagram Activities are already up to date")

    # If this is the first sync
    except KeyError:
        feed, next_url = api.user_recent_media(user_id=user_instagram_id)

    highest_found_id = ""
    lowest_found_id = ""
    while True:

        # Stop when there is an empty result set
        if not feed:
            break

        # For every item in the results set
        for media in feed:

            # Choose a proper Activity depeinding on the Media found
            if type == "video":
                activity_performed = Activity.objects.get(activity_name="Video Upload")
            else:
                activity_performed = Activity.objects.get(activity_name="Image Upload")

            # Assign the proper object used for the Activities
            object_used = "Instagram"

            # No goal can be found through these types of activities
            goal = ''
            goal_status = None

            # Construct a proper result based on the amount of likes and comments found
            try:
                number_of_comments = media.comment_count
            except:
                number_of_comments = 0

            try:
                number_of_likes = media.like_count
            except:
                number_of_likes = 0

            result = 'Your post has been liked by ' + str(number_of_likes) + \
                     ' and commented by ' + str(number_of_comments) + ' people at the moment'

            # Find the location (if it exists) that is related to this post
            try:
                location_address = media.location.name
                location_lat = media.location.point.latitude
                location_lng = media.location.point.longitude
            except AttributeError:
                location_lat = location_lng = None
                location_address = ''

            # The start and end date of the activity. We calculate a 2 minute interval due to the editing, captioning
            # etc. that each photograph or video subjects to
            start_date = datetime.strptime(str(media.created_time), "%Y-%m-%d %H:%M:%S") - timedelta(seconds=120)
            end_date = datetime.strptime(str(media.created_time), "%Y-%m-%d %H:%M:%S")

            # The friends related with the specific media (derive from tags). This field doesnt exist if it's empty
            try:
                friends_list = (list(set(media.users_in_photo)))
            except AttributeError:
                friends_list = ''

            # If it exists, remove the user from the list of friends (since he might have tagged himself)
            try:
                friends_list.remove(media.user.full_name)
            except ValueError:
                pass

            # The friends that participated in the Activity
            friends = ','.join(friends_list)

            performs_instance = addActivityFromProvider(user=user, activity=activity_performed, friends=friends,
                                    goal=goal, goal_status=goal_status, location_address=location_address,
                                    location_lat=location_lat, location_lng=location_lng, start_date=start_date,
                                    end_date=end_date, result=result, objects=object_used)

            # Store the activity "linking" in our database
            createActivityLinks('instagram', performs_instance, str(media.id), media.link)

        # get the IDs that will help optimize results of the next query
        if highest_found_id < feed[0].id:
            highest_found_id = str(int(feed[0].id.split('_')[0]) + 1) + '_' + feed[0].id.split('_')[1]

        if (lowest_found_id > feed[-1].id) or (not lowest_found_id):
            lowest_found_id = feed[-1].id

        # Get the next page of results. "Since_id" won't be assigned a value if we haven't synced before
        try:
            feed, next_url = api.user_recent_media(user_id=user_instagram_id, min_id=since_id, max_id=lowest_found_id)
        except UnboundLocalError:
            feed, next_url = api.user_recent_media(user_id=user_instagram_id, max_id=lowest_found_id)

    # Store user sync checkpoint inside the database
    social_auth_instance.extra_data['since_id'] = highest_found_id
    # Save everything
    social_auth_instance.save()

    return HttpResponse("Instagram Activities have been synced")


def syncYoutubeActivities(user):

    # The max amount of results that i ask the Youtube API to fetch me
    MAX_YOUTUBE_RESULTS = 5

    # The current api name of the provider
    YOUTUBE_API_NAME = 'youtube'

    # The current API version
    YOUTUBE_API_VERSION = 'v3'

    def fetchAndInsertVideoActivities(type, api, max_results):

         # We poll the Channels in order to get the ID of the "Watch History Channel" thats lets us access past seen videos
        channels = api.channels().list(part="contentDetails", mine=True).execute()

        # The ID of the selected Channel type. Can be 'watchHistory' or 'uploads'
        channel_type_id = channels['items'][0]['contentDetails']['relatedPlaylists'][type]

        # We poll the  Channel to get the  most recent watched or uploaded videos. The data returned DOESN'T
        # contain the durations of the videos or any other similar data so another call must be made
        channel_type_videos = api.playlistItems().list(part="snippet,contentDetails",
                                                            playlistId=channel_type_id,
                                                            maxResults=max_results).execute()

        # We create a comma-seperated list of the Ids of the 50 most recently watched or uploaded videos, based
        # on the value of the 'type' parameter
        channel_type_videoIds = ','.join(video['contentDetails']['videoId'] for video in channel_type_videos['items'])


        # We ask for the details (to get the Duration and Statistics) of the videos whose IDs are in the list above
        channel_type_video_details = api.videos().list(part="contentDetails,statistics",
                                                    id=channel_type_videoIds,
                                                        maxResults=max_results).execute()




        # The flag that lets us know we are done. It is triggered either by trying to add a previously added video
        # or by reaching the end of the video list
        more_new_videos_exist = True

        while more_new_videos_exist:

            # We iterate simultaneously through both lists, since each of them will give us an info the other cannot
            # provide. Specifically we get video duration from the 2nd and published (i.e. watched) date from the 1st
            for video, video_details in zip(channel_type_videos['items'], channel_type_video_details['items']):

                # The name of the performed activity
                if type == 'uploads':
                    activity_performed = Activity.objects.get(activity_name="Video Upload")
                else:
                    activity_performed = Activity.objects.get(activity_name="Video Watching")

                # The provider used for this activity
                object_used = "Youtube"

                # We can't get a goal for this activity, unless the user explicitly declares it
                goal = ""
                goal_status = None

                # The start date derives from the 1st list, while the end date is calculated via the duration of the video
                start_date = datetime.strptime(video['snippet']['publishedAt'][:-5], "%Y-%m-%dT%H:%M:%S")
                if type == 'uploads':
                    end_date = start_date + timedelta(seconds=300)
                else:
                    end_date = start_date + parseYoutubeDurationToTimedelta(video_details['contentDetails']['duration'])

                # Get the unique ID of the video in the provider's database
                video_id = video['contentDetails']['videoId']
                # The url that points to the actual Youtube video
                video_url = 'https://www.youtube.com/watch?v=' + video_id

                # Can't get any other participants in this type of Activity
                friends = ""

                # Can't get the location that the user watched the video. The only option was through their browser but
                # that not only isn't active all the time, but also gives a rather rough estimate of the actual location
                location_address = ""
                location_lat = location_lng = None

                # The result of this Activity
                result = "Including your activity, this video has been viewed " + \
                         str(video_details['statistics']['viewCount']) + " and liked " + \
                         str(video_details['statistics']['likeCount']) + " times in total"

                # Check if we reached the video that was inserted at a former Sync Action, then we are done here
                if PerformsProviderInfo.objects.filter(provider='youtube',
                                                       provider_instance_id=str(video_id)
                                                       ).count() > 0:
                    more_new_videos_exist = False
                    break

                # Add the activity to the database
                performs_instance = addActivityFromProvider(user=user, activity=activity_performed, friends=friends,
                                        goal=goal, goal_status=goal_status, location_address=location_address,
                                        location_lat=location_lat, location_lng=location_lng, start_date=start_date,
                                        end_date=end_date, result=result, objects=object_used)

                # Create a connection/link of the Activity representation between Activity Tracker and corresponding Provider
                createActivityLinks('youtube', performs_instance, str(video_id), video_url)

            # If we got here because we reached the end of the "new and not inserted" videos
            if not more_new_videos_exist:
                break

            # Try to get the next page of results
            try:
                channel_type_videos = api.playlistItems().list(part="snippet,contentDetails",
                                                               playlistId=channel_type_id,
                                                               nextPage=channel_type_videos['nextPageToken'],
                                                               maxResults=max_results).execute()

            # If there is not a next Page, stop iteration and return
            except:
                break


            # If there was a new page of results, proceed as normal
            channel_type_videoIds = ','.\
                join(video['contentDetails']['videoId'] for video in channel_type_videos['items'])

            channel_type_video_details = api.videos().list(part="contentDetails,statistics",
                                                    id=channel_type_videoIds,
                                                        maxResults=max_results).execute()

        return 'Ok'

    # Check if the user has de-authorized the App or the Secret Key has expired, and the page hasn't been refreshed
    social_auth_instance = user.social_auth.get(provider='youtube')
    if verifyInstagramAccess(social_auth_instance) != "Authentication Successful":
        return HttpResponse("Activity Tracker has been manually de-authorized from accessing Youtube")

    # The validated data needed by Google to produce an API object of Youtube
    credentials = AccessTokenCredentials(social_auth_instance.extra_data['access_token'], 'Activity-Tracker/1.0')

    # The api object of Youtube that corresponds to the current User
    api = build(YOUTUBE_API_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

    # Get and insert the video activities regarding uploaded videos
    fetchAndInsertVideoActivities('uploads', api, MAX_YOUTUBE_RESULTS)

    # Get and insert the video activities regarding recently watched videos
    fetchAndInsertVideoActivities('watchHistory', api, MAX_YOUTUBE_RESULTS)

    return HttpResponse("Youtube Activities have been synced")

def verifyRunkeeperAccess(social_auth_instance):
    if requests.get(
        url='http://api.runkeeper.com/user',
        headers={
            'Host': 'api.runkeeper.com',
            'Authorization': 'Bearer '+ str(social_auth_instance.extra_data['access_token']),
            'Accept': 'application/vnd.com.runkeeper.User+json'
        }
    ).status_code == 200:
        return 'Authentication Successful'
    else:
        return 'Authentication Failed'


def verifyTwitterAccess(social_auth_instance):
    try:
        api = tweetpony.API(consumer_key=SOCIAL_AUTH_TWITTER_KEY,
                        consumer_secret=SOCIAL_AUTH_TWITTER_SECRET,
                        access_token_secret=str(social_auth_instance.extra_data['access_token']['oauth_token_secret']),
                        access_token=str(social_auth_instance.extra_data['access_token']['oauth_token'])
        )
        return 'Authentication Successful'
    except APIError as error:
        if error.code == 88:
            return "Cannot Process Request"
        else:
            return 'Authentication Failed'


def verifyInstagramAccess(social_auth_instance):
   try:
        InstagramAPI(access_token=social_auth_instance.extra_data['access_token'],
                           client_secret=SOCIAL_AUTH_INSTAGRAM_SECRET)
        return 'Authentication Successful'
   except InstagramAPIError as error:
        if error.status_code in (420, 429):
            return 'Cannot Process Request'
        else:
            return 'Authentication Failed'


def verifyYoutubeAccess(social_auth_instance):

        # Check Access token
        google_authentication_url = 'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token='
        r = requests.get(google_authentication_url + social_auth_instance.extra_data['access_token']).json()

        if 'error_description' not in r:
            return 'Authentication Successful'

        # If there is an error, it might have expired. User the Refresh Token to fetch a new Access Token
        google_access_token_creator_url = 'https://www.googleapis.com/oauth2/v3/token'
        params = {'client_id': SOCIAL_AUTH_YOUTUBE_KEY,
                  'client_secret': SOCIAL_AUTH_YOUTUBE_SECRET,
                  'refresh_token': social_auth_instance.extra_data['refresh_token'],
                  'grant_type': 'refresh_token'
                  }
        r = requests.post(google_access_token_creator_url, params=params).json()

        # If the new Access Token is valid, store it in the database
        if 'error_description' not in r:
            social_auth_instance.extra_data['access_token'] = r['access_token']
            social_auth_instance.save()
            return 'Authentication Successful'

        # The 1st error wasn't because the Access Token had expired, but because the Authorization has been revoked by
        # the user. In this case there is nothing we can do, but wait for the user to re-authorize it manually
        else:
            return 'Authentication Failed'


def checkConnection(user, provider):
    try:
        social_auth_instance = user.social_auth.get(provider=provider)
        return  providerAuthenticationFunctions[provider](social_auth_instance)
    except ObjectDoesNotExist:
        return 'Not Connected'


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
    elif status == "Cannot Process Request":
        return {     'buttonText': 'Try again',
                     'buttonClassColor': 'grey',
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


# only providers that cant supply our app with activity data. Not providers for simply logging in
available_providers = ['twitter', 'runkeeper', 'instagram', 'youtube']
providerSyncFunctions = {
        'runkeeper': syncRunkeeperActivities,
        'twitter': syncTwitterActivities,
        'instagram': syncInstagramActivities,
        'youtube': syncYoutubeActivities,
        #'facebook': syncFacebookActivities,
        #'google': syncGoogleActivities
    }

providerAuthenticationFunctions = {
    'runkeeper': verifyRunkeeperAccess,
    'twitter': verifyTwitterAccess,
    'instagram': verifyInstagramAccess,
    'youtube': verifyYoutubeAccess,
}