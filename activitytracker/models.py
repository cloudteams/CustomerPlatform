from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Basic User model


class User(AbstractUser):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    gender = models.CharField(max_length=2,
                              choices=GENDER_CHOICES,
                              null=True
    )
    date_of_birth = models.DateField(null=True)



class UserVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    verification_code = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return '%s' %  self.verification_code

# Activity class with name

class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200,default="")
    icon_classname = models.CharField(max_length=50, default="")
    SELFCARE = 'black'
    COMMUNICATION = 'blue'
    SPORTS = 'greenLight'
    FUN = 'orange'
    RESPONSIBILITIES = 'redDark'
    TRANSPORTATION = 'purple'

    CATEGORY_CHOICES = (
        (SELFCARE, 'Self-care/Everyday Needs'),
        (COMMUNICATION, 'Communication/Socializing'),
        (SPORTS, 'Sports/Fitness'),
        (FUN, 'Fun/Leisure/Hobbies'),
        (RESPONSIBILITIES, 'Responsibilities'),
        (TRANSPORTATION, 'Transportation'),
    )
    category = models.CharField(max_length=20,
                                choices=CATEGORY_CHOICES,
                                null=True)

    def __str__(self):              # __unicode__ on Python 2
        return '%s' %  self.activity_name

# Simple object, M-to-N with Performs


class Object(models.Model):
    object_id = models.AutoField(primary_key=True)
    object_name = models.CharField(max_length=100)
    object_of_user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return '%s' % self.object_name

# Each Activity instance gets logged in the following class


class Performs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    activity = models.ForeignKey(Activity, db_column="activity_key")
    using = models.ManyToManyField(Object)
    goal = models.CharField(max_length=200)
    result = models.CharField(max_length=200, default='')
    friends = models.CharField(max_length=200)
    start_date = models.DateTimeField('Start Time')
    end_date = models.DateTimeField('End Time')
    STATUS_CHOICES = (
        ('Reached', 'Reached'),
        ('InProgress', 'In Progress'),
        ('Failed', 'Failed'),
    )
    goal_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True)
    location_address = models.CharField(max_length=200)
    location_lat = models.FloatField(null=True)
    location_lng = models.FloatField(null=True)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s %s %s' % (self.activity, self.goal, self.start_date, self.end_date)


    def correct_time(self):
        return self.end_date > self.start_date

    def duration(self):
        d = self.end_date - self.start_date
        days, seconds = d.days, d.seconds
        hours = seconds/3600
        minutes = (seconds - hours*3600)/60
        return [days, hours, minutes]

    def displayable_date(self):
        a = self.duration()
        if a[0] == 0:
            if a[1] == 0:
                return "%sm" % a[2]
            else:
                if a[2] == 0:
                    return "%sh" % a[1]
                else:
                    return "%sh%sm" % (a[1], a[2])
        else:
                if a[1] == 0:
                    if a[2] == 0:
                        return "%sd" % a[0]
                    else:
                        return "%sd%sm" % (a[0], a[2])
                else:
                    if a[2] == 0:
                        return "%sd%sh" % (a[0], a[1])
                    else:
                        return "%sd%sh%sm" % (a[0], a[1], a[2])

# class that associates activities of Activitytracker with activities of the provider
class PerformsProviderInfo(models.Model):
    instance = models.OneToOneField(Performs, related_name='instance')
    provider = models.CharField(max_length=100)
    provider_instance_id = models.CharField(max_length=50)

    def __str__(self):
        return '%d %s %s' % (self.instance.id, self.provider, self.provider_instance_id)


# Class for a simple friend list for each user, can then be hooked to Social Media profiles

class Friend(models.Model):
    friends_id = models.AutoField(primary_key=True)
    friend_name = models.CharField(max_length=100)
    friend_of_user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return '%s' % self.friend_name

# Class that lets the user define his basic Places/Locations
class Places(models.Model):
    place_id = models.AutoField(primary_key=True)
    place_name = models.CharField(max_length=200)
    place_address = models.CharField(max_length=200)

    place_lat = models.FloatField(null=True)
    place_lng = models.FloatField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("user", "place_name"),)

    def __str__(self):
        return '%s' % self.place_name


class hasSuperActivity(models.Model):
    superactivity = models.ForeignKey(Activity, related_name='superactivity')
    subactivity = models.ForeignKey(Activity, related_name='subactivity')

    def __str__(self):
        return '%s %s' % (self.super_activity, self.sub_activity)