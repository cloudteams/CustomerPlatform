from django import forms
from profile.models import UserProfile

__author__ = 'dipap'


class UserProfileForm(forms.ModelForm):
    location = forms.CharField()

    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if self.instance.user.first_name:
            self.initial['first_name'] = self.instance.user.first_name

        if self.instance.user.last_name:
            self.initial['last_name_initial'] = self.instance.user.last_name[0]

        if self.instance.user.date_of_birth:
            self.initial['year_of_birth'] = self.instance.user.date_of_birth.year

        if self.instance.user.location:
            self.initial['location'] = self.instance.user.location
