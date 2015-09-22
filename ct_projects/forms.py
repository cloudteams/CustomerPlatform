from ct_projects.models import Idea, IdeaRating
from django import forms

__author__ = 'dipap'


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        exclude = ['user', 'project_pk', ]


class IdeaRatingForm(forms.ModelForm):
    class Meta:
        model = IdeaRating
        fields = ['value', ]
