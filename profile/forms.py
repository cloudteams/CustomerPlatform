from django import forms

from profile.lists import *
from profile.models import UserProfile

__author__ = 'dipap'


class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('', 'I prefer not to say'),
    )
    gender = forms.RadioSelect(choices=GENDER_CHOICES)
    location = forms.CharField(required=False)

    # Influences
    influences = forms.MultipleChoiceField(choices=INFLUENCES, required=False)

    # Devices, platforms & interests
    devices = forms.MultipleChoiceField(choices=DEVICES, required=False)
    platforms = forms.MultipleChoiceField(choices=PLATFORMS, required=False)
    interests = forms.MultipleChoiceField(choices=INTERESTS, required=False)

    class Meta:
        model = UserProfile
        exclude = ('user', 'has_been_saved',)
        widgets = {
            'employment_status': forms.widgets.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if not self.instance.first_name and self.instance.user.first_name:
            self.initial['first_name'] = self.instance.user.first_name

        if not self.instance.last_name_initial and self.instance.user.last_name:
            self.initial['last_name_initial'] = self.instance.user.last_name[0]

        if not self.instance.year_of_birth and self.instance.user.date_of_birth:
            self.initial['year_of_birth'] = self.instance.user.date_of_birth.year

        if self.instance.user.location:
            self.initial['location'] = self.instance.user.location

        if self.instance.user.gender:
            self.initial['gender'] = self.instance.user.gender

        self.initial['influences'] = [influence.influence for influence in self.instance.user.influences.all()]
        self.initial['platforms'] = [platform_usages.platform for platform_usages in self.instance.user.platforms.all()]
        self.initial['devices'] = [device_usage.device for device_usage in self.instance.user.devices.all()]
        self.initial['interests'] = [user_interest.interest for user_interest in self.instance.user.interests.all()]
