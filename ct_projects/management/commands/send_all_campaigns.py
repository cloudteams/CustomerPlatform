
__author__ = 'dipap'

from django.core.management.base import BaseCommand
from ct_projects.models import Campaign
from ct_projects.connectors.team_platform.cloud_teams import CloudTeamsConnector


class Command(BaseCommand):
    help = 'Send all campaigns'

    def handle(self, *args, **options):
        # fetch all first
        CloudTeamsConnector().fetch_all()

        # send campaigns
        for campaign in Campaign.objects.all():
            try:
                self.stdout.write('Sending campaign #%d... ' % campaign.pk, ending='')
                self.stdout.flush()
                campaign.send()
                self.stdout.write("OK", ending='\n')
                self.stdout.flush()
            except:
                self.stdout.write("ERROR", ending='\n')
                self.stdout.flush()
