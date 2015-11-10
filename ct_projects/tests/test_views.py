from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_comments.forms import CommentForm
from activitytracker.models import User
from ct_projects.models import Idea

__author__ = 'dipap'


class ProjectViewsTestCase(TestCase):
    """
    The the Project entity
    """
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
    """
    Test following and unfollowing projects
    """
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


class IdeaTestCase(TestCase):
    """
    Test the Idea entity
    """
    def setUp(self):
        # create user
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

        # login
        self.client.post('/activitytracker/', data={'username': 'temporary', 'password': 'temporary'})

        # make sure i can post ideas to projects
        request = self.client.post(reverse('post-idea', args=('13417', )), data={
            'title': 'my idea',
            'description': 'this is an awesome idea'
        })
        self.assertEqual(request.status_code, 302)

    def test_create_idea(self):
        # assert fail on non-existing project
        request = self.client.post(reverse('post-idea', args=('13418', )), data={'title': 'my idea'})
        self.assertEqual(request.status_code, 404)
        # assert fail on missing description
        request = self.client.post(reverse('post-idea', args=('13417', )), data={'title': 'my idea'})
        self.assertEqual(request.status_code, 400)

    def test_view_idea(self):
        # test i can see the created idea
        request = self.client.get(reverse('idea-details', args=('13417', 1)))
        self.assertEqual(request.status_code, 200)

    def test_comment_on_idea(self):
        comment_post_url = '/projects/comments/post/'
        form = CommentForm(Idea.objects.get(pk=1))
        data = form.initial

        # verify i can't post some empty comment
        # unfortunately the framework returns a 200 OK response, so we have to check based on response contents
        request = self.client.post(comment_post_url, data=data)
        self.assertIn('This field is required.', request.content)

        # verify i can post some comment
        data['comment'] = 'nice!'
        request = self.client.post(comment_post_url, data=data)
        self.assertEqual(request.status_code, 302)

    def test_rating_idea(self):
        # test wrong value
        with self.assertRaises(ValueError):
            self.client.post(reverse('rate-idea', args=('13417', 1)), data={'value': 6})

        # verify i can rate an idea
        request = self.client.post(reverse('rate-idea', args=('13417', 1)), data={'value': 4})
        self.assertEqual(request.status_code, 302)

        idea = Idea.objects.get(pk=1)
        self.assertEqual(idea.get_rating_count(), 1)
        self.assertAlmostEqual(idea.get_average_rating(), 4)

        # verify i can rate an idea only once
        request = self.client.post(reverse('rate-idea', args=('13417', 1)), data={'value': 5})
        self.assertEqual(request.status_code, 403)


