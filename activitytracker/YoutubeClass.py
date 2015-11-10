from myfunctions import *
from AuthorizationChecks import *
from config import *
from django.db import transaction

class Youtube(OAuth2Validation):

    def __init__(self, user_social_instance):

        YOUTUBE_API_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'

        super(Youtube, self).__init__(user_social_instance)
        self.base_api_url = 'https://www.googleapis.com/%s/%s/' \
                            % (YOUTUBE_API_NAME,
                               YOUTUBE_API_VERSION
                               )

    @transaction.atomic()
    def _insertVideos(self, resource, videos, videos_details):

        _time_barrier = datetime.strptime(EARLIEST_DATA_DATE + ' 00:00:00',
                                          "%Y-%m-%d %H:%M:%S"
                                          )
        print videos
        for video, video_details in zip(videos['items'], videos_details):

            time_youtubed = start_date = datetime.strptime(video['snippet']['publishedAt'][:-5],
                                                           "%Y-%m-%dT%H:%M:%S"
                                                           )

            if time_youtubed < _time_barrier:
                return None, 'Reached Barrier'

            if not self.metadata.last_updated.startswith('0') \
               and time_youtubed <= datetime.strptime(self.metadata.last_updated,
                                                      "%Y-%m-%d %H:%M:%S"
                                                      ):
                return None, 'Reached End'

            if resource == 'uploads':

                activity_performed = Activity.objects.get(activity_name="Video Upload")
                end_date = start_date + timedelta(seconds=300)

            else:

                activity_performed = Activity.objects.get(activity_name="Video Watching")
                end_date = start_date + parseYoutubeDurationToTimedelta(video_details['contentDetails']['duration'])

            location_lat, location_lng, location_address = None, None, ''

            object_used = "Youtube"

            goal = ''
            goal_status = None

            friends = ''

            views = video_details['statistics']['viewCount'] if 'viewCount' in video_details['statistics'] else 0
            likes = video_details['statistics']['likeCount'] if 'likeCount' in video_details['statistics'] else 0
            result = "This video has been viewed %s and liked %s times in total" % (str(views), str(likes))

            video_id = video['contentDetails']['videoId']
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

        if 'nextPageToken' in videos:
            return videos['nextPageToken'], 'Ok'
        else:
            return None, 'Ok'

    def _findResource(self, resource):

        CHANNELS_ENDPOINT = 'channels'

        youtube_channels_endpoint = self.base_api_url + CHANNELS_ENDPOINT

        channels_params = {'access_token':self.provider_data['access_token'],
                           'mine': 'true',
                           'part': 'contentDetails'
                           }

        channels = requests.get(url=youtube_channels_endpoint,
                                params=channels_params
                                ).json()

        resource_id = channels['items'][0]['contentDetails']['relatedPlaylists'][resource]

        return resource_id

    def _fetchResourceData(self, resource):

        MAX_RESULTS = 50
        VIDEOS_ENDPOINT = 'videos'
        PLAYLIST_ITEMS_ENDPOINT = 'playlistItems'

        youtube_videos_endpoint = self.base_api_url + VIDEOS_ENDPOINT
        youtube_playlistItems_endpoint = self.base_api_url + PLAYLIST_ITEMS_ENDPOINT

        playlist_params = {'access_token':self.provider_data['access_token'],
                           'part': 'snippet,contentDetails',
                           'playlistId': self._findResource(resource),
                           'maxResults': MAX_RESULTS
                           }

        videos_params = {'access_token':self.provider_data['access_token'],
                         'part': 'contentDetails,statistics',
                         #'id': videoIds_string,
                         'maxResults': MAX_RESULTS
                         }

        while True:

            videos = requests.get(url=youtube_playlistItems_endpoint,
                                  params=playlist_params
                                  ).json()

            if 'error' in videos:
                return 'Error'

            videos_params['id'] = ','.join(video['contentDetails']['videoId'] for video in videos['items'])

            videos_details = requests.get(url=youtube_videos_endpoint,
                                          params=videos_params
                                          ).json()['items']

            if not videos:
                break

            next_page, status = self._insertVideos(resource, videos, videos_details)

            if next_page is None:
                break

            playlist_params['pageToken'] = next_page

        return 'Ok'

    def fetchData(self):

        fetched_resources = ['uploads', 'watchHistory']

        last_updated = str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        if self.validate() != 'Authentication Successful':
            return HttpResponseBadRequest(ERROR_MESSAGE)

        for resource in fetched_resources:

            outcome = self._fetchResourceData(resource)

            if outcome == "Error":
                return HttpResponseBadRequest(ERROR_MESSAGE)

        self.metadata.last_updated = last_updated
        self.metadata.save()

        return HttpResponse(self.PROVIDER.capitalize() + SUCCESS_MESSAGE)

