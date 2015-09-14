from django.test import TestCase
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector

__author__ = 'dipap'


class CloudTeamsConnectorTests(TestCase):

    def setUp(self):
        self.connector = CloudTeamsConnector()

    def test_list_projects(self):
        self.assertTrue(len(self.connector.list_projects()) > 0)

