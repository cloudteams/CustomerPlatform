from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction

class Fitbit(OAuth1Validation):

    def __init__(self, user_social_instance):
        super(Fitbit, self).__init__(user_social_instance)
        self.api_base_url = 'https://api.fitbit.com'

    def utcOffset(self, auth):

        FITBIT_PROFILE_DATA_URI = '/1/user/-/profile.json'

        profile_data_url = self.api_base_url + FITBIT_PROFILE_DATA_URI

        profile_data = requests.get(url=profile_data_url,
                                    auth=auth
                                    ).json()

        if 'offsetFromUTCMillis' not in profile_data['user']:
            return timedelta(seconds=0)

        return timedelta(milliseconds=profile_data['user']['offsetFromUTCMillis'])

    def _evaluateMealTime(self, meal_id):
        if meal_id == 1:
            start_time = '08:30:00'
            end_time = '08:50:00'
        elif meal_id == 2:
            start_time = '10:30:00'
            end_time = '10:40:00'
        elif meal_id == 3:
            start_time = '13:30:00'
            end_time = '14:00:00'
        elif meal_id == 4:
            start_time = '17:00:00'
            end_time = '17:10:00'
        elif meal_id == 5:
            start_time = '19:30:00'
            end_time = '20:00:00'
        else:
            start_time = '22:00:00'
            end_time = '22:15:00'

        return start_time, end_time

    @transaction.atomic()
    def _insertFoodActivities(self, feed):

        for activity in feed['foods']:

            if PerformsProviderInfo.objects.filter(provider='fitbit',
                                                   provider_instance_id=str(activity['logId'])
                                                   ).count() > 0:
                continue

            activity_performed = Activity.objects.get(activity_name='Eating')

            result = 'Consumed %s, which held %s calories in total' \
                     % (activity['loggedFood']['name'], activity['loggedFood']['calories'])

            friends = ''

            object_used = 'Fitbit'

            goal = 'Get %s calories today' % str(feed['goals']['calories'])
            goal_status = "InProgress"

            start_time, end_time = self._evaluateMealTime(activity['loggedFood']['mealTypeId'])

            start_date = '%s %s' % (activity['logDate'], start_time)
            end_date = '%s %s' % (activity['logDate'], end_time)

            location_address, location_lat, location_lng = '', None, None

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
                                provider_instance_id=str(activity['logId']),
                                url="https://www.fitbit.com/foods/log/%s"
                                    % activity['logDate'].replace('-', '/')
                                )

        return 'Ok'

    @transaction.atomic()
    def _insertSleepActivities(self, feed):

        for activity in feed['sleep']:

            if PerformsProviderInfo.objects.filter(provider='fitbit',
                                                   provider_instance_id=str(activity['logId'])
                                                   ).count() > 0:
                continue

            activity_performed = Activity.objects.get(activity_name='Sleeping')

            result = 'You had an %s%% efficient sleep. It took you %s minutes to fall asleep ' \
                     'and %s minutes to get out of bed after you woke up' \
                     % (str(activity['efficiency']),
                        str(activity['minutesToFallAsleep']),
                        str(activity['minutesAfterWakeup'])
                        )

            friends = ''

            object_used = 'Fitbit'

            goal = ''
            goal_status = None

            start_date = datetime.strptime(activity['startTime'], "%Y-%m-%d%%H:%M:%S.000")
            end_date = start_date + timedelta(milliseconds=activity['duration'])

            location_address, location_lat, location_lng = '', None, None

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
                                provider_instance_id=str(activity['logId']),
                                url="https://www.fitbit.com/sleep/%s"
                                    % activity['logDate'][:10].replace('-', '/')
                                )

        return 'Ok'

    @transaction.atomic()
    def _insertFitnessActivities(self, feed):

        for activity in feed:

            if not activity['hasStartTime']:
                continue

            if activity['name'] == "Run":
                activity_performed = Activity.objects.get(activity_name="Running")
            elif activity['name'] == "Walk":
                activity_performed = Activity.objects.get(activity_name="Walking")
            elif activity['name'] == "Hike":
                activity_performed = Activity.objects.get(activity_name="Hiking")
            else:
                activity_performed = Activity.objects.get(activity_name=activity['name'])

            location_lat, location_lng, location_address = None, None, ''

            object_used = "Fitbit"

            goal = ""
            goal_status = None

            friends = ''

            start_date = datetime.strptime(activity['startDate'] + activity['startTime'],
                                           "%Y-%m-%d%H:%M"
                                           )
            end_date = start_date + timedelta(milliseconds=activity['duration'])

            result = "Covered a distance of %s km in total. Burned %s calories." \
                     % (str(round(activity['distance'], 2)), str(activity['calories']))

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
                                provider_instance_id=str(activity['logId']),
                                url="https://www.fitbit.com/activities/exercise/%s"
                                    % activity['logId']
                                )

        return 'Ok'

    def fetchFitnessActivities(self, auth):

        FITBIT_FITNESS_URI = '/1/user/-/activities/list.json'

        last_sync = self.provider_data['last_updated']

        params = {'afterDate': last_sync.replace(' ', 'T'),
                  'sort': 'desc',
                  'limit': 100,
                  'offset': 0,
                  }

        if last_sync == DUMMY_LAST_UPDATED_INIT_VALUE + 'T00:00:00':
            params['afterDate'] = EARLIEST_DATA_DATE + 'T00:00:00'

        url = self.api_base_url + FITBIT_FITNESS_URI

        while True:

            fitness_feed = requests.get(url=url,
                                        params=params,
                                        auth=auth
                                        ).json()

            if 'errors' in fitness_feed:
                return 'Error'

            if not fitness_feed['activities']:
                break

            self._insertFitnessActivities(fitness_feed['activities'])

            if not fitness_feed['pagination']['next']:
                break

            params = {}
            url = fitness_feed['pagination']['next']

        return 'Ok'

    def fetchFoodActivities(self, auth):

        last_sync = self.provider_data['last_updated'][:10]

        if last_sync == DUMMY_LAST_UPDATED_INIT_VALUE:
            last_sync = EARLIEST_DATA_DATE

        chosen_day = (datetime.utcnow() + self.utcOffset(auth)).strftime("%Y-%m-%d")

        while True:

            if chosen_day < last_sync:
                break

            FITBIT_FOOD_URI = '/1/user/-/foods/log/date/%s.json' % chosen_day

            url = self.api_base_url + FITBIT_FOOD_URI

            food_feed = requests.get(url=url, auth=auth).json()

            if 'errors' in food_feed:
                return 'Error'

            if food_feed['foods']:
                self._insertFoodActivities(food_feed)

            chosen_day = (datetime.strptime(chosen_day, "%Y-%m-%d") - timedelta(days=1)).strftime('%Y-%m-%d')

        return 'Ok'

    def fetchSleepActivities(self, auth):

        last_sync = self.provider_data['last_updated'][:10]

        if last_sync == DUMMY_LAST_UPDATED_INIT_VALUE:
            last_sync = EARLIEST_DATA_DATE

        chosen_day = (datetime.utcnow() + self.utcOffset(auth)).strftime("%Y-%m-%d")

        while True:

            if chosen_day < last_sync:
                break

            FITBIT_SLEEP_URI = '/1/user/-/sleep/date/%s.json' % chosen_day

            url = self.api_base_url + FITBIT_SLEEP_URI

            sleep_feed = requests.get(url=url, auth=auth).json()
            print sleep_feed
            if 'errors' in sleep_feed:
                return 'Error'

            if sleep_feed['sleep']:
                self._insertSleepActivities(sleep_feed)

            chosen_day = (datetime.strptime(chosen_day, "%Y-%m-%d") - timedelta(days=1)).strftime('%Y-%m-%d')

        return 'Ok'

    def fetchData(self):

        if verify(self.user_social_instance) != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        auth = OAuth1(self.client_key,
                      self.client_secret,
                      self.resource_owner_key,
                      self.resource_owner_secret
                      )

        self.provider_data['last_updated'] = (datetime.utcnow() + self.utcOffset(auth)).strftime("%Y-%m-%d %H:%M:%S")

        status = self.fetchFitnessActivities(auth)

        if status != 'Ok':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        status = self.fetchFoodActivities(auth)

        if status != 'Ok':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        status = self.fetchSleepActivities(auth)

        if status != 'Ok':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        self.user_social_instance.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)