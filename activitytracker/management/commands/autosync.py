from django.core.management.base import BaseCommand, CommandError
from activitytracker.models import *
from activitytracker.views import *
from social.apps.django_app.default.models import *
from activitytracker.myfunctions import *
from activitytracker.AuthorizationChecks import *
from activitytracker.InstagramClass import Instagram
from activitytracker.TwitterClass import Twitter
from activitytracker.YoutubeClass import Youtube
from activitytracker.RunkeeperClass import Runkeeper
from activitytracker.FitbitClass import Fitbit
from activitytracker.FoursquareClass import Foursquare
import time
from config import *
import sched
from datetime import datetime as dt
import datetime


class Command(BaseCommand):
    help = 'Sync providers for all user once a day at midnight'

    def handle(self, *args, **options):
        def updateProvider():

            for provider in AVAILABLE_PROVIDERS:
                try:
                    user_set = UserSocialAuth.objects.filter(provider=provider)
                    for u in user_set:
                        user_object = u.user
                        social_instance = user_object.social_auth.get(provider=provider)
                        provider_object = eval(provider.capitalize())(social_instance)
                        provider_object.fetchData()
                except:
                    pass

            t = dt.combine(dt.now() + datetime.timedelta(days=1), daily_time)
            scheduler.enterabs(time.mktime(t.timetuple()), 1, updateProvider, ())

        # This code will only execute once per "autosync" command execution. Each type we manually need to restart the
        # autosync process this code will also run. It doesnt run when this command is up and running
        scheduler = sched.scheduler(time.time, time.sleep)
        daily_time = datetime.time(hour=06,minute=00)
        first_time = dt.combine(dt.now(), daily_time)
        scheduler.enterabs(time.mktime(first_time.timetuple()), 1, updateProvider, ())
        scheduler.run()
        self.stdout.write('Successfully started provider Autosync schedule')
