import json

import datetime
import requests
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_comments.models import Comment

from Activitytracker_Project.settings import ANONYMIZER_URL, PRODUCTION
from activitytracker.models import User
from ct_projects.connectors.cloud_teams.server_login import SERVER_URL, USER_PASSWD, CUSTOMER_PASSWD
from ct_projects.connectors.cloud_teams.xmlrpc_srv import XMLRPC_Server
from ct_projects.lists import POLL_TOKEN_STATES

from django.db import transaction


class Project(models.Model):
    """
    A CloudTeams Project
    Only exposed from projects API
    Teams Platform is responsible for posting to the API to keep project information up to date
    """
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    managers = models.TextField(blank=True, null=True, default=None)  # comma-separated list of usernames
    members = models.TextField(blank=True, null=True, default=None)  # comma-separated list of usernames
    created = models.DateTimeField(auto_now_add=True, editable=False)

    description = models.TextField(blank=True, null=True, default=None)
    logo = models.URLField(blank=True, null=True, default=None)
    category = models.TextField(blank=True, null=True, default=None)
    application_type = models.TextField(blank=True, null=True, default=None)
    rewards = models.TextField(blank=True, null=True, default=None)

    is_public = models.BooleanField(default=False)

    def get_running_campaigns(self):
        return [c for c in self.campaigns.all() if not c.has_expired()]

    def get_closed_campaigns(self):
        return [c for c in self.campaigns.all() if c.has_expired()]

    def get_related(self):
        # TODO implement related projects algorithm
        return Project.objects.all()[:3]

    def anonymize(self, user):
        """
        :param user: A user account in the CloudTeams Customer platform
        :return: The (first) persona user in which the user belongs in the context of this project
        """
        req = requests.get(ANONYMIZER_URL + '/persona-builder/api/find-user/?project=%d&user=%d' % (self.pk, user.pk))
        if req.status_code == 200:
            resp = json.loads(req.content)
            if 'persona' in resp:
                return resp
            else:
                return None
        else:
            return None

    def get_anonymized_username(self, user):
        u = self.anonymize(user)
        return '%s %s' % (u['first_name'], u['last_name'])

    def on_project_create(self):
        requests.post(ANONYMIZER_URL + '/persona-builder/api/init-project/', data={'project': self.pk})

    def to_json(self):
        return {
            'id': self.pk,
            'managers': self.managers.split(','),
            'members': self.members.split(','),
            'created': self.created,
            'name': self.title,
            'description': self.description,
            'category': self.category,
            'application_type': self.application_type,
            'rewards': self.rewards,
            'logo': self.logo,
            'is_public': self.is_public,
            'number_of_followers': self.followed.all().count(),
            'ideas': [idea.to_json() for idea in self.ideas.all()],
            'campaigns': [campaign.to_json() for campaign in self.campaigns.all()],
        }


@receiver(post_save, sender=Project)
def on_project_create(sender, instance, created, **kwargs):
    # Only on production
    if not PRODUCTION:
        return

    # Only when instance was created
    if created:
        instance.on_project_create()


class ProjectFollowing(models.Model):
    """
    A following relationship between a CloudTeams customer and a project
    """
    user = models.ForeignKey(User, related_name='follows')
    project = models.ForeignKey(Project, related_name='followed')
    created = models.DateTimeField(auto_now_add=True, editable=False)  # relationship timestamp


@receiver(post_save, sender=ProjectFollowing)
def on_project_following_create(sender, instance, created, **kwargs):
    # send notifications to the new user
    for campaign in instance.project.get_running_campaigns():
        campaign.send()

    # Only on production
    if not PRODUCTION:
        return

    if created:
        #XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD, verbose=0).set
        pass


@receiver(pre_delete, sender=ProjectFollowing)
def on_project_following_delete(sender, instance, **kwargs):
    # Only on production
    if not PRODUCTION:
        return

    #XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD, verbose=0).set


class Idea(models.Model):
    """
    An idea about a project
    """
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, related_name='ideas')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()

    comments = generic.GenericRelation(Comment, object_id_field='object_pk')

    def get_rating_count(self):
        return self.ratings.all().count()

    def get_average_rating(self):
        count = self.get_rating_count()
        if count > 0:
            result = self.ratings.all().aggregate(Sum('value'))['value__sum'] / (count + 0.0)
            return int(result*100) / 100.0
        else:
            return None

    def get_anonymized_username(self, user):
        return self.project.get_anonymized_username(user)

    def to_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'created': self.created,
            'updated': self.updated,
            'author': self.get_anonymized_username(self.user),
            'rating': self.get_average_rating(),
            'comments': [self.comment_to_json(c) for c in self.comments.all()],
        }

    def comment_to_json(self, comment):
        return {
            'author': self.get_anonymized_username(comment.user),
            'text': comment.comment,
            'created': comment.submit_date,
        }


class IdeaRating(models.Model):
    """
    The rating of an idea by a user
    """
    idea = models.ForeignKey(Idea, related_name='ratings')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class Campaign(models.Model):
    """
    A CloudTeams Campaign
    Each campaign is part of a project
    Teams Platform is responsible for posting to the API to keep campaign information up to date
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name='campaigns')
    description = models.TextField()
    starts = models.DateTimeField()
    expires = models.DateTimeField(blank=True, null=True, default=None)
    rewards = models.TextField(blank=True, null=True, default=None)
    logo = models.URLField(blank=True, null=True, default=None)

    def has_expired(self):
        if self.expires:
            return datetime.datetime.today() > self.expires

    def get_days_left(self):
        if self.has_expired():
            return None
        elif not self.expires:
            return None
        else:
            return (self.expires - datetime.datetime.today()).days

    def get_users(self):
        # get users to whom this item should be sent
        users = []
        req = requests.get(ANONYMIZER_URL + '/persona-builder/api/campaign-users/?campaign=%d' % self.pk)
        uids = json.loads(req.content)
        for uid in uids:
            try:
                users.append(User.objects.get(pk=uid))
            except User.DoesNotExist:
                pass

        # also add followers
        followers = [f.user for f in self.project.followed.all()]
        users += followers

        return users

    def send(self):
        # send notifications for all documents & polls
        users = self.get_users()

        for document in self.documents.all():
            document.send(users)

        for poll in self.polls.all():
            poll.send(users)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'starts': self.starts,
            'expires': self.expires,
            'rewards': self.rewards,
            'logo': self.logo,
        }


class Document(models.Model):
    """
    A CloudTeams Document
    Each document is part of a campaign
    Teams Platform is responsible for posting to the API to keep document information up to date
    """
    id = models.IntegerField(primary_key=True)
    campaign = models.ForeignKey(Campaign, related_name='documents')
    name = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)

    def get_absolute_url(self):
        return self.link

    def send(self, users=None):
        if not users:
            users = self.campaign.get_users()

        with transaction.atomic():
            for user in users:
                if not Notification.objects.filter(user=user, document=self).exists():
                    Notification.objects.create(user=user, document=self)


class Poll(models.Model):
    """
    A CloudTeams Poll
    Each poll is part of a campaign
    Teams Platform is responsible for posting to the API to keep poll information up to date
    Users get poll tokens to make sure we can later distribute awards
    """
    id = models.IntegerField(primary_key=True)
    campaign = models.ForeignKey(Campaign, related_name='polls')
    name = models.CharField(max_length=255)
    description = models.TextField()

    def request_token_link(self):
        return reverse('request-poll-token', args=(self.campaign.project.pk, self.pk))

    def get_poll_token_link(self, user):
        # get or create the link/user/persona combination
        try:
            token = PollToken.objects.get(poll=self, user=user)
        except PollToken.DoesNotExist:
            # find persona for user in the context of this project
            anonymous = self.campaign.project.anonymize(user)
            if anonymous:
                persona_id = anonymous['persona']
            else:
                persona_id = None

            # get the token link
            token_link = XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD, verbose=0).get_polltoken(str(self.id))

            # create the token object
            token = PollToken.objects.create(poll=self, user=user, persona_id=persona_id, token_link=token_link)

        return token.get_absolute_url()

    def send(self, users=None):
        if not users:
            users = self.campaign.get_users()

        with transaction.atomic():
            for user in users:
                if not Notification.objects.filter(user=user, poll=self).exists():
                    Notification.objects.create(user=user, poll=self)


class PollToken(models.Model):
    """
    The token that allows a CloudTeams customer to access a poll on Team Platform
    """
    token_link = models.URLField()
    poll = models.ForeignKey(Poll, related_name='tokens')
    user = models.ForeignKey(User, related_name='poll_tokens')
    persona_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=POLL_TOKEN_STATES, default='OPEN')

    def get_absolute_url(self):
        result = self.token_link
        if self.persona_id:
            result += '&persona=%d' % self.persona_id

        return result


class Notification(models.Model):
    """
    A notification regarding documents & polls
    """
    user = models.ForeignKey(User, related_name='notifications')
    document = models.ForeignKey(Document, blank=True, null=True, default=None)
    poll = models.ForeignKey(Poll, blank=True, null=True, default=None)
    seen = models.BooleanField(default=False)

    def message(self):
        if self.document:
            return self.document.name
        else:
            return self.poll.name

    def campaign(self):
        if self.document:
            return self.document.campaign
        else:
            return self.poll.campaign

    def url(self, user):
        if self.document:
            return self.document.get_absolute_url()
        else:
            return self.poll.get_poll_token_link(user)
