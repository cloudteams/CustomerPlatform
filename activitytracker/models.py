from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from social.apps.django_app.default.models import UserSocialAuth
from django.db.models import signals
import math

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
    location = models.CharField(max_length=200, null=True)
    logged_in_before = models.BooleanField(default=False)


class UserUniqueTokens(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=50)
    token_type = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s' %  (self.token, self.token_type)

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

    CATEGORY_ICONS = (
        ('sleeping', 'Self-care/Everyday Needs'),
        ('talking', 'Communication/Socializing'),
        ('running', 'Sports/Fitness'),
        ('coffee', 'Fun/Leisure/Hobbies'),
        ('teaching', 'Responsibilities'),
        ('public-transport', 'Transportation'),
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
    utc_offset = models.IntegerField(default=0)
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
        return '%s %s %s %s' % (self.activity, self.start_date, self.end_date, str(self.utc_offset))


    def correct_time(self):
        return self.end_date > self.start_date

    def duration(self):
        d = self.end_date - self.start_date
        days, seconds = d.days, d.seconds
        hours = seconds/3600
        minutes = int(math.ceil((seconds - hours*3600)/60.0))
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
    provider_instance_url = models.URLField(null=True)

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


class Routine(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    start_time = models.TimeField('Start Time', null=True)
    end_time = models.TimeField('End Time', null=True)
    seasonal_start = models.DateField(null=True)
    seasonal_end = models.DateField(null=True)
    DAY_TYPE_CHOICES = (
        ('Weekdays', 'Weekdays'),
        ('Weekend', 'Weekend'),
    )

    day_type = models.CharField(max_length=8,
                                choices=DAY_TYPE_CHOICES,
                                default='Weekdays')

    def __str__(self):
        return '%s %s | %s %s | %s - %s' % (
            self.user,
            self.activity,
            self.start_time,
            self.end_time,
            self.seasonal_start,
            self.seasonal_end
        )

class UserExtraProviderInfo(models.Model):
    social_instance = models.OneToOneField(UserSocialAuth)
    last_updated = models.CharField(max_length=20, default='0000-00-00 00:00:00')
    since_id = models.CharField(default='0', max_length=50)

    def __str__(self):
        return '%s %s %s %s' % (
            self.social_instance.user,
            self.social_instance.provider,
            self.last_updated,
            self.since_id

        )

def auto_create_user_provider_info(sender, instance, created, **kwargs):
    if created:
        self_instance = UserExtraProviderInfo(social_instance=instance)
        self_instance.save()


signals.post_save.connect(auto_create_user_provider_info, sender=UserSocialAuth)