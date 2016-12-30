
__author__ = 'dipap'

from django.core.management.base import BaseCommand
from ct_projects.models import Campaign
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector


class Command(BaseCommand):
    help = 'Fetch all projects, campaigns and developer replies from team platform'

    def handle(self, *args, **options):
        # fetch all projects
        CloudTeamsConnector().fetch_all()

