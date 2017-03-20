# -*- coding: utf-8 -*-
import json

import datetime
from xmlrpclib import Fault

import requests
import uuid as uuid
from django.contrib.contenttypes import generic
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.timezone import now
from django_comments.models import Comment

from Activitytracker_Project.settings import ANONYMIZER_URL, PRODUCTION, DEFAULT_FROM_EMAIL
from activitytracker.models import User
from ct_projects.connectors.cloudcoins import CloudCoinsClient
from ct_projects.connectors.cloudcoins.util import CloudCoinsAnswerAlreadyExistsError
from ct_projects.connectors.team_platform.server_login import SERVER_URL, USER_PASSWD, CUSTOMER_PASSWD
from ct_projects.connectors.team_platform.xmlrpc_srv import XMLRPC_Server
from ct_projects.lists import POLL_TOKEN_STATES, REWARD_TYPES

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
    icon = models.TextField(blank=True, null=True, default=None)
    application_type = models.TextField(blank=True, null=True, default=None)

    views = models.IntegerField(default=0)
    trend_factor = models.FloatField(default=0, db_index=True)
    is_public = models.BooleanField(default=False)

    # a comma-separated list of the contact emails
    contacts = models.TextField(blank=True, null=True, default=None)

    def get_contacts(self):
        if not self.contacts:
            return []

        return self.contacts.split(',')

    def increase_views(self):
        Project.objects.filter(pk=self.pk).update(views=self.views + 1)

    def update_trend_factor(self):
        tf = (self.get_running_campaigns().__len__() * 10 + self.number_of_followers * 5 + self.ideas.all().count() * 3 + self.views + 1.0) / \
             ((now() - self.created).days + 1.0)

        Project.objects.filter(pk=self.pk).update(trend_factor=tf)

    def get_running_campaigns(self):
        return [c for c in self.campaigns.all() if not c.has_expired()]

    def get_closed_campaigns(self):
        return [c for c in self.campaigns.all() if c.has_expired()]

    def get_related(self):
        related = Project.objects.filter(category=self.category).exclude(pk=self.pk)[:3]

        if not related:
            related = Project.objects.filter(application_type=self.application_type).exclude(pk=self.pk)[:3]

        if not related:
            related = Project.objects.all().exclude(pk=self.pk)[:3]

        return related

    def count_rewards(self):
        return self.rewards.all().count()

    def anonymize(self, user):
        """
        :param user: A user account in the CloudTeams Customer platform
        :return: The (first) persona user in which the user belongs in the context of this project
        """
        req = requests.get(ANONYMIZER_URL + '/team-ideation-tools/api/find-user/?project=%d&user=%d' % (self.pk, user.pk))
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
        requests.post(ANONYMIZER_URL + '/team-ideation-tools/api/init-project/', data={'project': self.pk})

    @property
    def number_of_followers(self):
        return self.followed.all().count()

    def update_number_of_followers(self, on_delete=False):
        # Only on production
        if not PRODUCTION:
            return

        try:
            cnt = self.followed.all().count()
            if on_delete:
                cnt -= 1

            XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD).setfollowers(str(self.id), str(cnt))
        except Fault:
            print('Error on updating number of followers for project #%d' % self.id)

    def update_number_of_likes(self, on_delete=False):
        # Only on production
        if not PRODUCTION:
            return

        try:
            cnt = self.likes.all().count()
            if on_delete:
                cnt -= 1

            XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD).setlikes(str(self.id), str(cnt))
        except Fault:
            print('Error on updating number of followers for project #%d' % self.id)

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
            'logo': self.logo,
            'is_public': self.is_public,
            'number_of_followers': self.number_of_followers,
            'ideas': [idea.to_json() for idea in self.ideas.all()],
            'campaigns': [campaign.to_json() for campaign in self.campaigns.all()],
        }

    def __unicode__(self):
        return self.title


@receiver(post_save, sender=Project)
def on_project_create(sender, instance, created, **kwargs):
    # Only on production
    if not PRODUCTION:
        return

    # Only when instance was created
    if created:
        instance.on_project_create()


@receiver(pre_delete, sender=Project)
def on_project_delete(sender, instance, *args, **kwargs):
    """
    Notifies customers following the project it was deleted
    Fixed issue https://github.com/cloudteams/CloudTeams_Issues/issues/195
    """
    followers = User.objects.filter(pk__in=instance.followed.all().values_list('user_id', flat=True))
    with transaction.atomic():
        for follower in followers:
            Notification.objects.create(user=follower,
                                        text='Project %s was unpublished from CloudTeams' % instance.title)


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

    if created:
        instance.project.update_number_of_followers()


@receiver(pre_delete, sender=ProjectFollowing)
def on_project_following_delete(sender, instance, **kwargs):
    instance.project.update_number_of_followers(on_delete=True)


class ProjectLike(models.Model):
    """
    A user likes a project
    """
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, related_name='likes')


@receiver(post_save, sender=ProjectLike)
def on_project_like(sender, instance, created, **kwargs):

    if created:
        instance.project.update_number_of_likes()


@receiver(pre_delete, sender=ProjectLike)
def on_project_unlike(sender, instance, **kwargs):
    instance.project.update_number_of_likes(on_delete=True)


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

    class Meta:
        ordering = ['-created']

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

    def on_idea_create(self):
        message = self.title + '\n' + self.description
        try:
            XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD).add_post(str(self.project.id), message)
        except Fault:
            print('Could not post idea to team platform')


class BlogPost(models.Model):
    """
    A blog entry posted by the team for a project
    """
    project = models.ForeignKey(Project, related_name='blogs')
    created = models.DateTimeField()
    title = models.CharField(max_length=1024)
    image_link = models.CharField(max_length=1024, default='')
    author = models.CharField(max_length=1024, default='')
    content = models.TextField()

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return '%s (Posted by %s under "%s")' % (self.title, self.author, self.project.title)

    def get_absolute_url(self):
        return '/projects/%s/blogs/%s/' % (str(self.project_id), str(self.pk))


@receiver(post_save, sender=Idea)
def on_idea_posted(sender, instance, created, **kwargs):
    # Only on production
    if not PRODUCTION:
        return

    # Only when idea was created
    if created:
        instance.on_idea_create()


class IdeaRating(models.Model):
    """
    The rating of an idea by a user
    """
    idea = models.ForeignKey(Idea, related_name='ratings')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class ProjectManager(models.Model):
    """
    Very basic info for a project manager
    """
    email = models.EmailField()


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
    actual_close = models.DateTimeField(blank=True, null=True, default=None)  # used when manually closed
    logo = models.URLField(blank=True, null=True, default=None)
    closed = models.BooleanField(default=False)

    # coins info
    answer_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, default=None)
    manager = models.ForeignKey(ProjectManager, blank=True, null=True, default=None)
    max_answers = models.IntegerField(blank=True, null=True, default=None)

    def close_time(self):
        return self.actual_close or self.expires

    def has_expired(self):
        if self.closed:
            return True

        if self.expires:
            return datetime.datetime.today() > self.expires

        return False

    def try_to_reopen(self):
        if datetime.datetime.today() <= self.expires:
            if self.max_answers is not None:
                if self.max_answers > self.count_participants():
                    self.closed = False
            else:
                self.closed = False

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
        req = requests.get(ANONYMIZER_URL + '/team-ideation-tools/api/campaign-users/?campaign=%d' % self.pk)
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

    def count_participants(self):
        return PollToken.objects.filter(poll__campaign=self).count()

    def has_participated(self, user):
        return self in user.get_participated_campaigns()

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
            'logo': self.logo,
        }

    @staticmethod
    def send_all():
        campaigns = Campaign.objects.filter(expires__gt=datetime.datetime.today(), closed=False)
        for campaign in campaigns:
            campaign.send()

        print('%d campaign%s sent' % (len(campaigns), '' if len(campaigns) == 1 else 's'))

    def save(self, *args, **kwargs):

        # for closed campaigns, cancel notifications
        if self.pk and self.has_expired():
            Notification.objects.\
                filter(Q(poll__campaign_id=self.pk) | Q(document__campaign_id=self.pk)). \
                update(dismissed=True)

        super(Campaign, self).save(*args, **kwargs)

    def get_results_url(self):
        try:
            return self.polls.all()[0].get_results_url()
        except IndexError:
            return None

    def __str__(self):
        return '%s (%s)' % (self.name, 'closed' if self.has_expired() else 'open')


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

    def get_results_url(self):
        if not self.campaign.has_expired():
            return None

        try:
            token = PollToken.objects.filter(poll__campaign_id=self.campaign_id, status='DONE')[0]
        except IndexError:
            return None

        return token.token_link + '&mode=votes'

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

    def update_coins(self):
        if self.status == 'DONE' and self.poll.campaign.answer_value > 0:
            try:
                CloudCoinsClient().campaigns.add_answer(campaign_id=self.poll.campaign_id, user_id=self.user_id)
            except CloudCoinsAnswerAlreadyExistsError:
                # here we don't care if answer was already posted
                pass

            # maybe campaign now must be closed
            campaign = self.poll.campaign
            if campaign.max_answers is not None:
                if campaign.max_answers <= campaign.count_participants():
                    campaign.closed = True
                    campaign.actual_close = now()
                    campaign.save()

            # create success popup notification
            message = '[P]You just earned <i class="icon icon-cloudcoins"></i> %d CC !<br />' % \
                      self.poll.campaign.answer_value
            Notification.objects.create(user_id=self.user_id, text=message, persistent=False)


@receiver(post_save, sender=PollToken)
def on_poll_token_saved(sender, instance, created, **kwargs):
    # when token is completed
    if instance.status == 'DONE':
        instance.update_coins()


class RewardPurchaseError(ValueError):
    """
    Error type for when an exception happens while buying a reward, or for when a reward can not be bought
    """
    pass


class Reward(models.Model):
    """
    A reward offered by a project
    """
    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey(Project, related_name='rewards')
    reward_type = models.CharField(max_length=32, choices=REWARD_TYPES)
    image_link = models.CharField(max_length=1024, default='')
    download_ref = models.CharField(max_length=1024, default='')
    name = models.CharField(max_length=512)
    description = models.TextField()

    # logistics
    cost = models.IntegerField(validators=[MinValueValidator(1)])
    total_amount = models.IntegerField(validators=[MinValueValidator(1)])
    given = models.IntegerField(validators=[MinValueValidator(0)])
    remaining = models.IntegerField(validators=[MinValueValidator(0)])

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return '%s' % self.name

    @staticmethod
    def available_rewards(user=None):
        qs = Reward.objects.filter(is_available=True)

        # for user, exclude bough rewards
        if user:
            qs = qs.exclude(sales__user_id=user.pk)

        # least remaining first
        qs = qs.order_by('remaining')

        return qs

    def get_all_links(self):
        # each line contains another reward link
        result = self.download_ref.split('\n')[:self.total_amount]

        # fill in missing rewards
        if result.__len__() < self.total_amount:
            result += [result[-1]] * (self.total_amount - result.__len__())

        return result

    def get_link_for_user(self, user):
        rps = RewardPurchase.objects.filter(reward=self).order_by('pk')

        idx = None
        for i, rp in enumerate(rps):
            if rp.user == user:
                idx = i
                break

        if idx is None:
            return None

        try:
            return self.get_all_links()[idx]
        except IndexError:
            return None

    def purchase(self, buyer):

        # check if already bought
        if RewardPurchase.objects.filter(user=buyer, reward=self).exists():
            raise RewardPurchaseError('You have already bought this reward.')

        # check stock
        if self.remaining < 1:
            raise RewardPurchaseError('Reward has been sold out.')

        # check balance
        if buyer.balance < self.cost:
            raise RewardPurchaseError('You don\'t have enough CloudCoins!')

        # Only on production
        if PRODUCTION:
            # notify team platform another reward is sold
            try:
                XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD).give_reward(str(self.project_id), str(self.id))
            except Fault:
                raise RewardPurchaseError('Reward has been sold out.')

        # create purchase entry
        purchase = RewardPurchase.objects.create(user=buyer, reward=self, coins_spent=self.cost)

        # update customer balance
        # TODO make call to CC service to update balance

        # update info
        self.given += 1
        self.remaining -= 1

        if self.remaining <= 0:
            self.is_available = False

        self.save()

        return purchase


class RewardPurchase(models.Model):
    """
    A user bought a reward
    """
    user = models.ForeignKey(User, related_name='bought_rewards')
    reward = models.ForeignKey(Reward, related_name='sales')
    coins_spent = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return '<User %s> bought %s' % (self.user.username, str(self.reward))


class ContactRequest(models.Model):
    """
    A customer wants to contact a project team
    """
    user = models.ForeignKey(User, related_name='contact_requests')
    project = models.ForeignKey(Project, related_name='contact_requests')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    provided_info = models.TextField(blank=False)
    message = models.TextField()

    def send_email(self):
        # send the email
        from_email = DEFAULT_FROM_EMAIL
        mail_title = 'CloudTeams - A customer is interested in %s' % self.project.title

        recipient = [contact.encode('utf8') for contact in self.project.get_contacts()]
        mail_message = get_template('profile/emails/contact-team.txt').render({
            'title': 'New customer contact',
            'project': self.project,
            'contact_request': self
        })
        mail_html_message = get_template('profile/emails/contact-team.html').render({
            'title': 'New customer contact',
            'project': self.project,
            'contact_request': self
        })

        send_mail(mail_title, mail_message, from_email, recipient, html_message=mail_html_message, fail_silently=False)


class Notification(models.Model):
    """
    A notification with its context and actions
    """
    user = models.ForeignKey(User, related_name='notifications')
    document = models.ForeignKey(Document, blank=True, null=True, default=None)
    poll = models.ForeignKey(Poll, blank=True, null=True, default=None)

    # custom notifications
    text = models.TextField(default='')
    custom_action = models.TextField(default='')
    custom_action_text = models.TextField(default='')
    dismiss_action = models.TextField(default='')

    seen = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    persistent = models.BooleanField(default=True)

    def message(self):
        if self.document:
            return self.document.name
        elif self.poll:
            return self.poll.name
        else:
            return self.text

    def campaign(self):
        if self.document:
            return self.document.campaign
        elif self.poll:
            return self.poll.campaign
        else:
            return None

    def url(self):
        if self.document:
            return self.document.get_absolute_url()
        elif self.poll:
            return self.poll.get_poll_token_link(self.user)
        else:
            return None

    def main_action_text(self):
        if self.document:
            return 'Open document'
        elif self.poll:
            return 'Participate'
        elif self.custom_action and self.custom_action_text:
            return self.custom_action_text
        else:
            return 'OK'

    def dismiss_action_text(self):
        if self.dismiss_action:
            return self.dismiss_action
        elif self.document or self.poll or self.custom_action:
            return 'Dismiss'
        else:
            return 'OK'

    def perform_custom_action(self, generic_redirect=True):
        redirect_to = '/profile/notifications/'

        if not self.custom_action:
            return

        if self.custom_action.find('FOLLOW ') == 0:
            try:
                project_id = int(self.custom_action.split(' ')[1])
                project = Project.objects.get(id=project_id)
                if not self.user.follows.filter(project_id=project_id).exists():
                    ProjectFollowing.objects.create(user=self.user, project=project)

                if not generic_redirect:
                    redirect_to = '/projects/%d/' % project_id
            except:
                pass

        return redirect_to

    def send_email(self):
        # validate that email should be sent
        if not self.poll:
            return None

        # expired
        if self.poll.campaign.has_expired():
            return None

        # user has already participated
        if self.poll.campaign.has_participated(user=self.user):
            return None

        # user has disabled notifications
        if not self.user.profile.email_notifications:
            return None

        # already sent
        if NotificationEmail.objects.filter(notification=self).exists():
            return

        from django.utils.translation import activate
        activate('en')

        # send the email
        email = DEFAULT_FROM_EMAIL
        mail_title = "[New CloudTeams Campaign] %s needs YOUR help!" % self.poll.campaign.project.title

        recipient = [self.user.email.encode('utf8')]
        mail_message = get_template('profile/notification/email.txt').render({
            'notification': self,
        })
        mail_html_message = get_template('profile/notification/email.html').render({
            'notification': self,
        })

        send_mail(mail_title, mail_message, email, recipient, html_message=mail_html_message, fail_silently=False)

        # mark as sent
        return NotificationEmail.objects.create(notification=self)

    def __unicode__(self):
        return 'Notification to %s about "%s"' % (self.user.username, self.message())


class NotificationEmail(models.Model):
    """
    A notification was sent by email
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    notification = models.ForeignKey(Notification, related_name='emails')

    @staticmethod
    def send_emails(log=True):
        # get pending notifications
        qs = Notification.objects. \
            filter(persistent=True, dismissed=False). \
            exclude(user__email__iendswith='@test.com'). \
            exclude(poll=None). \
            filter(poll__campaign__expires__gt=now()). \
            filter(emails=None)

        # make sure no user receives more than one email
        users = {}
        for notification in qs:
            if notification.user.username not in users:
                users[notification.user.username] = []

            users[notification.user.username].append(notification)

        for username in users.keys():
            for notification in users[username]:

                # send at maximum one email
                if notification.send_email():

                    if log:
                        print(notification)

                    break


def get_participated_campaigns(user, project=None):
    # completed polls
    ps = PollToken.objects.filter(user=user).exclude(poll=None).filter(status='DONE')
    if project:
        ps = ps.filter(poll__campaign__project=project)

    campaign_ids = list(set(ps.values_list('poll__campaign', flat=True)))

    # opened documents
    """
    ds = PollToken.objects.filter(user=user).exclude(document=None).filter(status='USED')
    if project:
        ds = ds.filter(document__campaign__project=project)

    campaign_ids += list(set(ds.values_list('poll__campaign', flat=True)))
    """

    # return campaign objects
    return Campaign.objects.filter(id__in=campaign_ids)

User.get_participated_campaigns = get_participated_campaigns


@property
def all_notifications(user):
    return [n for n in Notification.objects.filter(user=user, persistent=True, dismissed=False).order_by('-created')
            if (not n.campaign()) or
                ((not n.campaign().has_expired()) and
                 (n.campaign() not in user.get_participated_campaigns()))]

User.all_notifications = all_notifications


@property
def get_balance(user):
    costs = RewardPurchase.objects.filter(user_id=user.pk).aggregate(total_cost=Sum('coins_spent'))['total_cost'] or 0

    return CloudCoinsClient().users.get(customer_id=user.pk).balance - costs

User.balance = get_balance
