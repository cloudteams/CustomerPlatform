from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
from django.db.models import Sum
from activitytracker.models import User


class Project:

    def __init__(self, pk, title, description, publisher):
        self.pk = pk
        self.title = title
        self.description = description
        self.publisher = publisher

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'<#%s - %s>' % (self.pk, self.title)

    def ideas(self):
        return Idea.objects.filter(project_pk=self.pk)


class BSCWProject(models.Model):
    """
    A BSCW Project
    Only exposed from projects API
    BSCW is responsible for posting to the API to keep project information up to date
    """
    owner_username = models.CharField(max_length=255)
    team_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    logo = models.URLField(blank=True, null=True, default=None)

    def to_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'logo': self.logo,
            'owner_username': self.owner_username,
            'team_name': self.team_name,
            'created': self.created,
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
    project_pk = models.IntegerField(validators=[MinValueValidator(0)])
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


class IdeaRating(models.Model):
    """
    The rating of an idea by a user
    """
    idea = models.ForeignKey(Idea, related_name='ratings')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
