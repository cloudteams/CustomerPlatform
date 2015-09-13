from myfunctions import *
from AuthorizationChecks import *
from config import *
from django.db import transaction


class Gmail(OAuth2Validation):

    def __init__(self, user_social_instance):

        super(Gmail, self).__init__(user_social_instance)
        self.user_email_api_url = 'https://www.googleapis.com/gmail/v1/users/me/messages'

    @transaction.atomic()
    def _insertShoppingActivities(self, emails):

        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00',
                                          "%Y-%m-%d %H:%M:%S"
                                          )

        params = {'access_token': self.provider_data['access_token']}

        for email in emails['messages']:
            message_url = self.user_email_api_url + '/%s' % email['id']

            message = requests.get(url=message_url, params=params).json()

            if 'error' in message:
                return 'Error'

            print message
            continue

            time_received = start_date = datetime.strptime(email['snippet']['publishedAt'][:-5],
                                                           "%Y-%m-%dT%H:%M:%S"
                                                           )

            if time_received < _time_barrier:
                return None, 'Reached Barrier'

            if not self.metadata.last_updated.startswith('0') \
               and time_received <= datetime.strptime(self.metadata.last_updated,
                                                      "%Y-%m-%d %H:%M:%S"
                                                      ):
                return None, 'Reached End'

            activity_performed = Activity.objects.get(activity_name="Video Watching")
            end_date = start_date + parseYoutubeDurationToTimedelta(video_details['contentDetails']['duration'])

            location_lat, location_lng, location_address = None, None, ''

            object_used = "Gmail"

            goal = ''
            goal_status = None

            start_date = time_received - timedelta(seconds=120)
            end_date = time_received

            friends = ''

            result = "This video has been viewed %s and liked %s times in total" \
                     % (str(emil['statistics']['viewCount']),
                        str(email['statistics']['likeCount'])
                        )

            video_id = email['contentDetails']['videoId']
            video_url = 'https://www.youtube.com/watch?v=' + video_id

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
                                provider_instance_id=str(video_id),
                                url=video_url
                                )

        if 'nextPageToken' in emails:
            return emails['nextPageToken'], 'Ok'
        else:
            return None, 'Ok'

    def fetchData(self):

        MAX_RESULTS = 1

        sync_time = str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        params = {'access_token':self.provider_data['access_token'],
                  'includeSpamTrash': 'false',
                  'maxResults': MAX_RESULTS,
                  }

        while True:

            emails = requests.get(url=self.user_email_api_url, params=params).json()

            if 'error' in emails:
                return HttpResponseBadRequest(ERROR_MESSAGE)

            if not emails['messages']:
                break

            next_page, status = self._insertShoppingActivities(emails)

            if status == 'Error':
                return HttpResponseBadRequest(ERROR_MESSAGE)

            if next_page is None:
                break

            return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)
            params['pageToken'] = next_page

        self.metadata.last_updated = sync_time
        self.metadata.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)