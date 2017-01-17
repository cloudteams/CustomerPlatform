
__author__ = 'dipap'

from django.core.management.base import BaseCommand
from ct_projects.models import NotificationEmail


class Command(BaseCommand):
    help = 'Send pending notification emails'

    def handle(self, *args, **options):
        NotificationEmail.send_emails()

