from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction

class FacebookActivity(OAuth2Validation):

    def __init__(self, user_social_instance):
        super(FacebookActivity, self).__init__(user_social_instance)
        self.api_user_timeline_url = 'https://graph.facebook.com/v2.4/me/posts'

    @transaction.atomic()
    def _insertMedia(self, feed):

        _max_id = 0
        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00', "%Y-%m-%d %H:%M:%S")

        for media in feed:

            time_posted = datetime.strptime(media['created_time'], '%Y-%m-%dT%H:%M:%S+0000')

            if time_posted < _time_barrier:
                return _max_id, 'Reached Barrier'

            if media['type'] == "status":
                activity_performed = Activity.objects.get(activity_name="Status Update")

            elif media['type'] == "photo" and media['status_type'] == 'added_photo':
                activity_performed = Activity.objects.get(activity_name="Status Update")

            elif media['type'] == "video" and media['status_type'] == 'added_video':
                activity_performed = Activity.objects.get(activity_name="Video Upload")

            else:
                activity_performed = Activity.objects.get(activity_name="Share / Retweet")

            # IMPORTANT: Only counting comments on the original post.
            # Not comment-replies to other comments of the post
            result = 'Your post has been liked by %s and commented by %s people' % (
                media['likes']['summary']['total_count'],
                media['comments']['summary']['total_count']
            )

            if 'place' in media:
                if 'location' in media['place']:
                    location_address = media['place']['location']['street']
                    location_lat = media['place']['location']['latitude']
                    location_lng = media['place']['location']['longitude']
                else:
                    location = Geocoder.geocode(media['place']['name'])
                    location_address = media['place']['name']
                    location_lat = location.latitude
                    location_lng = location.longitude
            else:
                location_lat, location_lng, location_address = None, None, ''

            object_used = "Facebook" + ',Smartphone' if media['status_type'] == 'mobile_status_update' else ''

            goal = ''
            goal_status = None

            start_date = time_posted - timedelta(seconds=60)
            end_date = time_posted

            tags = list()

            for key, tag_list in media['story_tags']:
                for tag in tag_list:
                    tags.append(tag['name'])

            for key, tag_list in media['with_tags']:
                for tag in tag_list:
                    tags.append(tag['name'])

            tags = list(set(tags))
            tags.remove('')
            #tags.remove('username')

            friends = ','.join(tags)

            performs_instance = addActivityFromProvider(user=self.user,
                                                        activity=activity_performed,
                                                        friends=friends,
                                                        goal=goal, goal_status=goal_status,
                                                        location_address=location_address,
                                                        location_lat=location_lat,
                                                        location_lng=location_lng,
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        result=result,
                                                        objects=object_used
                                                        )
            # To be confirmed
            if media['id'] > self.provider_data['since_id']:
                self.provider_data['since_id'] = media['id']

            # To be fixed
            if (_max_id > feed[-1]['id']) or (_max_id == 0):
                _max_id = feed[-1]['id']

            media_url = 'www.facebook.com/' + media['id']
            createActivityLinks(provider=self.PROVIDER.lower(),
                                instance=performs_instance,
                                provider_instance_id=str(media['id']),
                                url=media_url
                                )

        return _max_id, 'Ok'

    def fetchData(self):

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        params = {'access_token': self.provider_data['access_token'],
                  'fields': 'created_time,type,status_type,place,likes.summary(true),comments.summary(true),story_tags,with_tags'
        }

        """
        if self.provider_data['last_updated'] != DUMMY_LAST_UPDATED_INIT_VALUE:
            params['min_id'] = self.provider_data['since_id']

        self.provider_data['last_updated'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        while True:
            # ok
            response = requests.get(url=self.api_user_timeline_url, params=params).json()
            #ok
            feed = response['data']
            #ok
            if not feed:
                break
            #ok
            if 'error' in response:
                return HttpResponse(ERROR_MESSAGE)

            params['max_id'], status = self._insertMedia(feed)

            if status == "Barrier Reached":
                break

        self.user_social_instance.save()
        """

        response = requests.get(url=self.api_user_timeline_url, params=params).json()
        print response

        # I still need to get the checkins, both personal and from other people. Also need access to posts of photos
        # or videos by others that i have been tagged in.
        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)
