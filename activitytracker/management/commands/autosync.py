from django.core.management.base import BaseCommand, CommandError
from activitytracker.models import *
from activitytracker.views import *
from social.apps.django_app.default.models import *
from activitytracker.myfunctions import *
import time
import sched
from datetime import datetime as dt
import datetime


class Command(BaseCommand):
    help = 'Sync providers for all user once a day at midnight'

    def handle(self, *args, **options):
        def updateProvider():
            for provider_name in available_providers:
                try:
                    user_set = UserSocialAuth.objects.filter(provider=provider_name)
                    for u in user_set:
                        user_object = u.user
                        if checkConnection(user_object, provider_name) == "Authentication Successful":
                            providerSyncFunctions[provider_name](user_object)
                except:
                    pass

            t = dt.combine(dt.now() + datetime.timedelta(days=1), daily_time)
            scheduler.enterabs(time.mktime(t.timetuple()), 1, updateProvider, ())
        scheduler = sched.scheduler(time.time, time.sleep)
        daily_time = datetime.time(hour=06,minute=00)
        first_time = dt.combine(dt.now(), daily_time)
        scheduler.enterabs(time.mktime(first_time.timetuple()), 1, updateProvider, ())
        scheduler.run()
        self.stdout.write('Successfully started provider Autosync schedule')
