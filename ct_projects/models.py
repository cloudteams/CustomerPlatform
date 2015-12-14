from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
from django.db.models import Sum
from activitytracker.models import User


class Project(models.Model):
    """
    A CloudTeams Project
    Only exposed from projects API
    Teams Platform is responsible for posting to the API to keep project information up to date
    """
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    project_managers = models.TextField()  # comma-separated list of usernames
    project_members = models.TextField(blank=True, null=True, default=None)  # comma-separated list of usernames
    created = models.DateTimeField(auto_now_add=True, editable=False)

    description = models.TextField(blank=True, null=True, default=None)
    logo = models.URLField(blank=True, null=True, default=None)
    category = models.TextField(blank=True, null=True, default=None)
    application_type = models.TextField(blank=True, null=True, default=None)
    rewards = models.TextField(blank=True, null=True, default=None)

    is_public = models.BooleanField(default=False)

    def to_json(self):
        return {
            'id': self.pk,
            'project_manager': self.project_manager,
            'project_members': self.project_members,
            'created': self.created,
            'name': self.title,
            'description': self.description,
            'category': self.category,
            'application_type': self.application_type,
            'rewards': self.rewards,
            'logo': self.logo,
            'is_public': self.is_public,
            'number_of_followers': ProjectFollowing.objects.filter(project_pk=self.pk).count(),
            'ideas': [idea.to_json() for idea in self.ideas.all()],
            'campaigns': [campaign.to_json() for campaign in self.campaigns.all()],
        }


class ProjectFollowing(models.Model):
    """
    A following relationship between a CloudTeams customer and a project
    """
    user = models.ForeignKey(User)
    project_pk = models.IntegerField(validators=[MinValueValidator(0)])
    created = models.DateTimeField(auto_now_add=True, editable=False)  # relationship timestamp


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

    def get_rating_count(self):
        return self.ratings.all().count()

    def get_average_rating(self):
        count = self.get_rating_count()
        if count > 0:
            return self.ratings.all().aggregate(Sum('value'))['value__sum'] / (count + 0.0)
        else:
            return None

    def get_anonymized_username(self):
        # TODO use anonymized usernames in project ideas
        return self.user.username

    def to_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'created': self.created,
            'updated': self.updated,
            'author': self.get_anonymized_username(),
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
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name='campaigns')
    description = models.TextField()
    expires = models.DateTimeField()
    rewards = models.TextField(blank=True, null=True, default=None)
    logo = models.URLField(blank=True, null=True, default=None)
    campaign_type = models.CharField(max_length=31, default='Questionnaire')
    content_url = models.URLField()

    def to_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'expires': self.expires,
            'rewards': self.rewards,
            'logo': self.logo,
            'campaign_type': self.campaign_type,
            'content_url': self.content_url,
        }
