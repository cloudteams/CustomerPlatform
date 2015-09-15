from django import template
from ct_projects.models import ProjectFollowing

__author__ = 'dipap'

register = template.Library()


@register.filter
def is_followed_by(project, user):
    return ProjectFollowing.objects.filter(project_pk=project.pk, user=user).count() > 0
