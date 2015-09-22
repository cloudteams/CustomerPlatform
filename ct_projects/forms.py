from ct_projects.models import Idea
from django import forms

__author__ = 'dipap'


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        exclude = ['user', 'project_pk', ]
