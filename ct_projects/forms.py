from ct_projects.models import Idea, IdeaRating, BSCWProject
from django import forms

__author__ = 'dipap'


class BSCWProjectForm(forms.ModelForm):
    class Meta:
        model = BSCWProject
        exclude = ['created', ]


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        exclude = ['user', 'project_pk', ]


class IdeaRatingForm(forms.ModelForm):
    class Meta:
        model = IdeaRating
        fields = ['value', ]
