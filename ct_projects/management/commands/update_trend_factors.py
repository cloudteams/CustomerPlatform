
__author__ = 'dipap'

from django.core.management.base import BaseCommand
from ct_projects.models import Project


class Command(BaseCommand):
    help = 'Updates the trand factor of all existing projects'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            project.update_trend_factor()

