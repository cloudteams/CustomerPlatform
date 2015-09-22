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
        return self.ideas.all().count()

    def get_average_rating(self):
        count = self.get_rating_count
        if count:
            return self.ideas.all().aggregate(Sum('value')) / (count + 0.0)
        else:
            return None


class IdeaRating(models.Model):
    """
    The rating of an idea by a user
    """
    idea = models.ForeignKey(Idea, related_name='ideas')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
