from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction

class Runkeeper(OAuth2Validation):

    def __init__(self, user_social_instance):
        super(Runkeeper, self).__init__(user_social_instance)
        self.api_base_url = 'http://api.runkeeper.com'

    @transaction.atomic()
    def _insertFitnessActivities(self, feed):

        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00', "%Y-%m-%d %H:%M:%S")

        for item_ in feed:

            if PerformsProviderInfo.objects.filter(provider='runkeeper',
                                                   provider_instance_id=item_['uri']
                                                   ).count() > 0:
                continue

            activity = requests.get(url=self.api_base_url + item_['uri'],
                                    params={'access_token': self.provider_data['access_token']}
                                    ).json()

            time_monitored = datetime.strptime(activity['start_time'], '%a, %d %b %Y %H:%M:%S')

            if time_monitored < _time_barrier:
                return 'Reached Barrier'

            activity_performed = Activity.objects.get(activity_name=activity['type'])

            result = ''

            if 'total_distance' in activity:
                result += 'Covered %s meters in total. ' % str(int(round(activity['total_distance'])))

            if 'total_calories' in activity:
                result += 'Burned %s calories.' % str(int(round(activity['total_calories'])))

            if 'path' in activity:

                location_lat = float(activity['path'][0]['latitude'])
                location_lng = float(activity['path'][0]['longitude'])
                location_address = str(Geocoder.reverse_geocode(location_lat, location_lng))

            else:
                location_address, location_lat, location_lng = '', None, None

            goal = ''
            goal_status = None

            friends = ''

            start_date = time_monitored
            end_date = time_monitored + timedelta(seconds=activity['duration'])

            object_used = "Runkeeper"
            if activity['equipment'] != "None":
                object_used += ',' + activity['equipment']

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
                                provider_instance_id=activity['uri'],
                                url=activity['activity']
                                )

        return 'Ok'

    def fetchData(self):

        RUNKEEPER_FITNESS_URI = '/fitnessActivities'

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        request_url = self.api_base_url + RUNKEEPER_FITNESS_URI
        params = {'access_token': self.provider_data['access_token']}

        if self.provider_data['last_updated'] != DUMMY_LAST_UPDATED_INIT_VALUE:
            params['noEarlierThan'] = self.provider_data['last_updated'][:10]

        self.provider_data['last_updated'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        while True:

            feed = requests.get(url=request_url,
                                params=params
                                ).json()

            if not feed:
                break

            if 'items' not in feed:
                return HttpResponseBadRequest(ERROR_MESSAGE)

            status = self._insertFitnessActivities(feed['items'])

            if (status == "Barrier Reached") or ('next' not in feed):
                break

            request_url = self.api_base_url + feed['next']

        self.user_social_instance.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)
