from random import randint

from profile.models import UserProfile


import datetime
from time import sleep

from django.core.management import BaseCommand

from ct_projects.models import Campaign


class Command(BaseCommand):
    help = 'Updates test accounts with employment/education info'

    def handle(self, *args, **options):
        test_profiles = UserProfile.objects.filter(user__username__startswith='user', user__email__endswith='@test.com')

        for tp in test_profiles:
            if randint(0, 10) == 1:
                tp.education = 'I prefer not to say'
            elif randint(0, 100) < 3:
                tp.education = 'Elementary'
            elif randint(0, 100) % 2 == 0:
                tp.education = 'Secondary'
            else:
                tp.education = 'Tertiary'
            if randint(0, 10) <= 1:
                tp.employment_status = 'Employed'
            elif randint(0, 10) == 0:
                tp.employment_status = 'Unemployed'
            elif randint(0, 10) <= 1:
                tp.employment_status = 'Student'
            elif randint(0, 100) <= 5:
                tp.employment_status = 'I prefer not to say'
            elif randint(0, 100) <= 9:
                tp.employment_status = 'Pensioner'
            elif randint(0, 10) <= 3:
                tp.employment_status = 'Self-employed'
            else:
                tp.employment_status = 'Employed'

            UserProfile.objects.filter(pk=tp.pk).update(education=tp.education,
                                                        employment_status=tp.employment_status)