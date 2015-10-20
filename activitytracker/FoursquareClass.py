from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction
import time

class Foursquare(OAuth2Validation):

    def __init__(self, user_social_instance):
        super(Foursquare, self).__init__(user_social_instance)
        self.api_user_checkin_history_url = 'https://api.foursquare.com/v2/users/self/checkins'
        self.parameters = {'oauth_token': self.provider_data['access_token'],
                           'v': '20150728'
                           }

    @transaction.atomic()
    def _insertCheckInActivities(self, feed):

        for checkin in feed:

            if PerformsProviderInfo.objects.filter(provider='foursquare',
                                                   provider_instance_id=checkin['id']
                                                   ).count() > 0:
                continue

            activity_performed = Activity.objects.get(activity_name='Check-In')

            time_monitored = datetime.utcfromtimestamp(checkin['createdAt'])

            result = ''

            if checkin['like']:
                result += 'You liked this place. '

            result += 'Your check-in resulted into a total of %s for this place' \
                      % checkin['venue']['stats']['checkinsCount']

            location_lat = float(checkin['venue']['location']['lat'])
            location_lng = float(checkin['venue']['location']['lng'])
            location_address = checkin['venue']['name']

            goal = ''
            goal_status = None

            friends = ''

            if 'with' in checkin:
                friends = ','.join('%s %s' % (friend['firstName'],
                                              friend['lastName']
                                              ) for friend in checkin['with']
                                   )

            start_date = time_monitored - timedelta(seconds=60)
            end_date = time_monitored

            object_used = "Foursquare"

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

            createActivityLinks(provider=self.PROVIDER.lower(),
                                instance=performs_instance,
                                provider_instance_id=checkin['id'],
                                url='https://foursquare.com/user'
                                )

        return 'Ok'

    def fetchData(self):

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        params = {'oauth_token': self.provider_data['access_token'],
                  'limit': 250,
                  'offset': 0,
                  'v': '20150728',
                  'sort': 'newestfirst',
                  'afterTimestamp': int(time.mktime(
                                           datetime.strptime(
                                               EARLIEST_DATA_DATE + ' 00:00:00',
                                               '%Y-%m-%d %H:%M:%S'
                                               ).timetuple())
                                           )
                  }

        if self.metadata.last_updated != DUMMY_LAST_UPDATED_INIT_VALUE:
            params['afterTimestamp'] = int(time.mktime(
                                           datetime.strptime(
                                                self.metadata.last_updated,
                                               '%Y-%m-%d %H:%M:%S'
                                               ).timetuple())
                                           )

        self.metadata.last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        while True:

            response = requests.get(url=self.api_user_checkin_history_url,
                                    params=params
                                    ).json()

            if not response['response']['checkins']['items']:
                break

            if 'errorType' in response['meta']:
                return HttpResponseBadRequest(ERROR_MESSAGE)

            status = self._insertCheckInActivities(response['response']['checkins']['items'])

            params['offset'] += params['limit']

        self.metadata.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)
