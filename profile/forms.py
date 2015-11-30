from django import forms
from profile.models import UserProfile

__author__ = 'dipap'


class UserProfileForm(forms.ModelForm):
    location = forms.CharField(required=False)

    class Meta:
        model = UserProfile
        exclude = ('user', 'has_been_saved',)

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
