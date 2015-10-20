from myfunctions import *
from AuthorizationChecks import *
from django.db import transaction

class Twitter(OAuth1Validation):

    def __init__(self, user_social_instance):
        super(Twitter, self).__init__(user_social_instance)
        self.api_user_timeline_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

    @transaction.atomic()
    def _insertTweets(self, tweets):

        _max_id = 0
        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00', "%Y-%m-%d %H:%M:%S")

        for tweet in tweets:

            time_tweeted = datetime.strptime(str(tweet['created_at']), "%a %b %d %H:%M:%S +0000 %Y")

            if time_tweeted < _time_barrier:
                return _max_id, 'Reached Barrier'

            if tweet['retweeted']:

                activity_performed = Activity.objects.get(activity_name="Share / Retweet")
                result = "%s Including yours, there is a total of %s retweets at the moment." \
                         % ('You have favorited this tweet.' if tweet['favorited'] else '',
                            str(tweet['retweet_count'])
                            )

            else:

                activity_performed = Activity.objects.get(activity_name="Status Update")
                result = " Your tweet has been retweeted %s and favorited %s times" \
                         % (str(tweet['retweet_count']),
                            str(tweet['favorite_count'])
                            )

            if tweet['coordinates'] is not None:

                location_lat = tweet['coordinates']['coordinates'][1]
                location_lng = tweet['coordinates']['coordinates'][0]
                location_address = str(Geocoder.reverse_geocode(location_lat, location_lng)[0])

            elif tweet['place'] is not None:

                location_lat = (tweet['place']['bounding_box']['coordinates'][0][0][1] \
                               + tweet['place']['bounding_box']['coordinates'][0][2][1]) /2.0
                location_lng = (tweet['place']['bounding_box']['coordinates'][0][0][0] \
                               + tweet['place']['bounding_box']['coordinates'][0][1][0]) /2.0
                location_address = tweet['place']['full_name']

            else:

                location_lat, location_lng, location_address = None, None, ''

            object_used = "Twitter"

            goal = ""
            goal_status = None

            start_date = time_tweeted - timedelta(seconds=60)
            end_date = time_tweeted

            friends_list = (list(set([mention['name'] for mention in tweet['entities']['user_mentions']])))
            friends_list.remove(tweet['user']['name']) if tweet['user']['name'] in friends_list else True
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

            if (tweet['id'] -1 < _max_id) or (_max_id == 0):

                _max_id = tweet['id'] - 1

            if tweet['id'] > self.metadata.since_id:
                self.metadata.since_id = tweet['id']

            createActivityLinks(provider=self.PROVIDER.lower(),
                                instance=performs_instance,
                                provider_instance_id=str(tweet['id']),
                                url="https://twitter.com/statuses/%s" % tweet['id_str']
                                )

        return _max_id, 'Ok'

    def fetchData(self):

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        auth = OAuth1(self.client_key,
                      self.client_secret,
                      self.resource_owner_key,
                      self.resource_owner_secret
                      )

        params = {'user_id': self.provider_id,
                  'count': 200,
                  'trim_user': False,
                  'include_rts': True,
                  'exclude_replies': False,
                  'contributor_details': True,
                  }

        if self.metadata.last_updated != DUMMY_LAST_UPDATED_INIT_VALUE:
            params['since_id'] = self.metadata.since_id

        self.metadata.last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        while True:
            print self.api_user_timeline_url
            print params

            tweets = requests.get(url=self.api_user_timeline_url,
                                  params=params,
                                  auth=auth
                                  ).json()
            print tweets
            if not tweets:
                break

            if 'errors' in tweets:
                return HttpResponse(ERROR_MESSAGE)

            params['max_id'], status = self._insertTweets(tweets)

            if status == "Barrier Reached":
                break

        self.metadata.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)