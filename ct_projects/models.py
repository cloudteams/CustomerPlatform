from django.core.validators import MinValueValidator
from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
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


class ProjectFollowing(models.Model):
    """
    A following relationship between a CloudTeams customer and a project
    """
    user = models.ForeignKey(User)
    project = models.IntegerField(validators=[MinValueValidator(0)])
