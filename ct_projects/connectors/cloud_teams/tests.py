from django.test import TestCase
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector

__author__ = 'dipap'


class CloudTeamsConnectorTests(TestCase):

    def setUp(self):
        self.connector = CloudTeamsConnector()

    def test_list_projects(self):
        project_list = self.connector.list_projects()
        self.assertTrue(len(project_list) > 0)
        self.assertTrue(project_list[0].pk >= 0)

    def test_get_project(self):
        self.assertNotEqual(self.connector.get_project('13417'), None)
        self.assertEqual(self.connector.get_project('13418'), None)
