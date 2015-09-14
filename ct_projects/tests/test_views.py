from django.test import TestCase

__author__ = 'dipap'


class ProjectViewsTestCase(TestCase):

    def test_projects_home(self):
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
