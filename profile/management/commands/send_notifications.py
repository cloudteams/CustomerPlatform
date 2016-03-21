import datetime
from time import sleep

from django.core.management import BaseCommand

from ct_projects.models import Campaign


class Command(BaseCommand):
    help = 'Sends notifications for running campaigns'

    def handle(self, *args, **options):
        while True:
            campaigns = Campaign.objects.filter(expires__gt=datetime.datetime.today())
            for campaign in campaigns:
                campaign.send()

            print('%d campaign%s sent' % (len(campaigns), '' if len(campaigns) == 1 else 's'))

            # wait for a minute
            sleep(60)
