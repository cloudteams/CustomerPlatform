from ct_projects.models import Idea, IdeaRating, Project
from django import forms

__author__ = 'dipap'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['created', ]


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        exclude = ['user', 'project', ]


class IdeaRatingForm(forms.ModelForm):
    class Meta:
        model = IdeaRating
        fields = ['value', ]
