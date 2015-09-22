from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.test import TestCase
from activitytracker.models import User

__author__ = 'dipap'


class ProjectViewsTestCase(TestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

        # login
        self.client.post('/activitytracker/', data={'username': 'temporary', 'password': 'temporary'})

    def test_projects_home(self):
        response = self.client.get(urlresolvers.reverse('all-projects'))
        self.assertEqual(response.status_code, 200)

    def test_followed_home(self):
        response = self.client.get(urlresolvers.reverse('followed-projects'))
        self.assertEqual(response.status_code, 200)


class ProjectFollowingTestCase(TestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

        # login
        self.client.post('/activitytracker/', data={'username': 'temporary', 'password': 'temporary'})

    def test_project_follow(self):
        # make sure I can follow an existing project
        post = self.client.post(reverse('follow-project', args=('13417', )))
        self.assertEqual(post.status_code, 302)

        # I shouldn't be able to follow a project that does not exist
        post = self.client.post(reverse('follow-project', args=('13418', )))
        self.assertEqual(post.status_code, 404)

        # I shouldn't be able to follow a project multiple times
        post = self.client.post(reverse('follow-project', args=('13417', )))
        self.assertEqual(post.status_code, 403)

    def test_project_unfollow(self):
        # follow an existing project
        post = self.client.post(reverse('follow-project', args=('13417', )))
        self.assertEqual(post.status_code, 302)

        # make sure I can un-follow a project I folow
        post = self.client.post(reverse('unfollow-project', args=('13417', )))
        self.assertEqual(post.status_code, 302)

        # make sure I can un-follow a project that doesn't exist
        post = self.client.post(reverse('unfollow-project', args=('13418', )))
        self.assertEqual(post.status_code, 404)

        # make sure I can un-follow a project that I don't follow
        post = self.client.post(reverse('unfollow-project', args=('13417', )))
        self.assertEqual(post.status_code, 403)

    def test_project_details(self):
        # view an existing project
        request = self.client.get(reverse('project-details', args=('13417', )))
        self.assertEqual(request.status_code, 200)
        # view a non-existing project
        request = self.client.get(reverse('project-details', args=('13418', )))
        self.assertEqual(request.status_code, 404)
