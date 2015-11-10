from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from activitytracker.models import User
from profile.lists import BUSINESS_SECTORS, WORK_POSITIONS, INFLUENCES, DEVICES, PLATFORMS, BRAND_OPINIONS, \
    TECH_LEVELS
from profile.multiple_choice_field import MultiSelectField

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class UserProfile(models.Model):
    """
    Additional information about CloudTeams customer account
    Initially will be filled in using the wizard
    """

    # Link to user in Activity Tracker
    user = models.OneToOneField(User)

    # Avatar
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True, default=None)

    # Generic info
    first_name = models.CharField(max_length=255)
    last_name_initial = models.CharField(max_length=1)
    year_of_birth = models.IntegerField(blank=True, null=True, default=None, validators=[MinValueValidator(1930),
                                                                                         MaxValueValidator(2010)])
    # -- location is in main model -> asume it to be home location

    # Business info
    business_sector = models.CharField(max_length=127, blank=True, default='', choices=BUSINESS_SECTORS)
    work_position = models.CharField(max_length=127, blank=True, default='', choices=WORK_POSITIONS)
    work_location = models.CharField(max_length=255, blank=True, default='')
    years_experience = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])

    # Influences
    influences = MultiSelectField(max_length=16, blank=True, default='', choices=INFLUENCES)

    # Devices & platforms
    devices = MultiSelectField(max_length=2, blank=True, default='', choices=DEVICES)
    platforms = MultiSelectField(max_length=8, blank=True, default='', choices=PLATFORMS)

    # Tech level
    tech_level = models.CharField(max_length=8, blank=True, default='', choices=TECH_LEVELS)

    # Check if the profile wizard has run at least once
    has_been_saved = models.BooleanField(default=False, editable=False)

    def get_display_name(self):
        return '%s %s.' % (self.first_name, self.last_name_initial)


class UserBrandOpinion(models.Model):
    user = models.ForeignKey(User, related_name='brand_opinions')
    brand = models.CharField(max_length=16)
    opinion = models.CharField(max_length=1, choices=BRAND_OPINIONS)
