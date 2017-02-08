from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction

class Instagram(OAuth2Validation):

    def __init__(self, user_social_instance):
        super(Instagram, self).__init__(user_social_instance)
        self.api_user_timeline_url = 'https://api.instagram.com/v1/users/self/media/recent/'

    @transaction.atomic()
    def _insertMedia(self, feed):

        _max_id = 0
        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00', "%Y-%m-%d %H:%M:%S")

        for media in feed:

            time_posted = datetime.utcfromtimestamp(float(media['created_time']))

            if time_posted < _time_barrier:
                return _max_id, 'Reached Barrier'

            if media['type'] == "video":
                activity_performed = Activity.objects.get(activity_name="Video Upload")
            else:
                activity_performed = Activity.objects.get(activity_name="Image Upload")

            result = 'Your post has been liked by %s and commented by %s people' \
                     % (media['likes']['count'], media['comments']['count'])

            if media['location'] is not None:

                location_address = media['location']['name']
                location_lat = media['location']['latitude']
                location_lng = media['location']['longitude']

            else:

                location_lat, location_lng, location_address = None, None, ''

            object_used = "Instagram"

            goal = ''
            goal_status = None

            start_date = time_posted - timedelta(seconds=120)
            end_date = time_posted

            friends_list = [user_mention['user']['full_name'] for user_mention in media['users_in_photo']]
            friends_list.remove(media['user']['full_name'] ) if media['user']['full_name'] in friends_list else True
            friends = ','.join(friends_list)

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

            if feed[0]['id'] > self.metadata.since_id:
                self.metadata.since_id = str(int(feed[0]['id'].split('_')[0]) + 1) \
                                                 + '_' + feed[0]['id'].split('_')[1]

            if (_max_id > feed[-1]['id']) or (_max_id == 0):
                _max_id = feed[-1]['id']

            createActivityLinks(provider=self.PROVIDER.lower(),
                                instance=performs_instance,
                                provider_instance_id=str(media['id']),
                                url=media['link']
                                )

        return _max_id, 'Ok'

    def fetchData(self):

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        params = {'access_token': self.provider_data['access_token']}

        if self.metadata.last_updated != DUMMY_LAST_UPDATED_INIT_VALUE and self.metadata.since_id != '0':
            params['min_id'] = self.metadata.since_id

        last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        while True:

            response = requests.get(url=self.api_user_timeline_url, params=params).json()

            feed = response['data']

            if not feed:
                break

            if 'error_type' in response['meta']:
                return HttpResponse(ERROR_MESSAGE)

            params['max_id'], status = self._insertMedia(feed)

            if status == "Barrier Reached":
                break

        self.metadata.last_updated = last_updated
        self.metadata.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)
