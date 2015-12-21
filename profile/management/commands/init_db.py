import random
from random import randint
import string
from datetime import date, datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.db import transaction
from django.utils.timezone import UTC, now

from activitytracker.models import User, Activity, Performs
from profile.lists import BUSINESS_SECTORS, INFLUENCES, DEVICES, PLATFORMS
from profile.models import UserProfile, UserBrandOpinion, DeviceUsage, Influence, PlatformUsage
__author__ = 'dipap'


# lists of names
name_folder = 'profile/management/commands/data/'
male_names = open(name_folder + 'male_names.txt').read().split('\n')
female_names = open(name_folder + 'female_names.txt').read().split('\n')

NOW = now()


def get_random_date(after=None, before=NOW):
    d = datetime(year=2015 - randint(0, 2), month=randint(1, 12), day=randint(1, 28), hour=randint(0, 23),
                 minute=randint(0, 59), second=randint(0, 59))

    if after and before:
        if after > before:
            raise Exception('Impossible datetime range')
        if (d < before) and (d > after):
            return d
        else:
            return get_random_date()
    elif after:
        if d > after:
            return d
        else:
            return get_random_date()
    elif before:
        if d < before:
            return d
        else:
            return get_random_date()
    else:
        return d
    
    
class Command(BaseCommand):
    help = 'Initializes the database with random data [Note: Existing database contents will be erased]'
    option_list = BaseCommand.option_list + (
        make_option(
            "-u",
            "--users",
            dest="users",
            help="specify the number of users",
            metavar="USERS"
        ),
        make_option(
            "-H",
            "--host",
            dest="host",
            help="set the host (e.g localhost:8000)",
            metavar="HOST"
        ),
    )

    def handle(self, *args, **options):
        if not options['users']:
            n_of_users = 800
        else:
            try:
                n_of_users = int(options['users'])
            except ValueError:
                raise CommandError("Option `--users=...` must be an integer.")

        # Remove previous data
        print('Cleaning database...')
        User.objects.all().delete()
        print('Done')

        # Create test users
        print('Creating test users...')
        with transaction.atomic():
            password = make_password('pass123')
            for x in range(1, n_of_users+1):
                username = 'user' + str(x)
                user = User.objects.create(username=username, password=password, email='user' + str(x) + '@test.com')
                UserProfile.objects.create(user=user)
                print('\t' + username)
        print('Done')

        # load activities
        activities = Activity.objects.all()[:]

        # Fill their profile
        print('Creating profiles...')
        with transaction.atomic():
            for profile in UserProfile.objects.all():
                # general info - gender, name, age
                profile.user.gender = 'M' if randint(1, 2) == 1 else 'F'
                if profile.user.gender == 'M':
                    names = male_names
                else:
                    names = female_names
                profile.first_name = names[randint(1, len(names) - 1)]
                profile.last_name_initial = random.choice(string.ascii_letters).upper()

                # people under 35 are 80% of our user base (ok, just an assumption here)
                current_year = date.today().year
                if randint(1, 10) <= 8:
                    profile.year_of_birth = randint(current_year - 35, current_year - 15)
                else:
                    profile.year_of_birth = randint(current_year - 60, current_year - 35)

                # work - only one in two have given this info
                if randint(1, 2) == 1:
                    profile.business_sector = BUSINESS_SECTORS[randint(2, len(BUSINESS_SECTORS) - 1)][0]

                # tech level - again, one in two
                if randint(1, 2) == 1:
                    if randint(1, 10) <= 2:  # 20%
                        profile.tech_level = 'Beginner'
                    elif randint(1, 2) == 1:  # 40%
                        profile.tech_level = 'Intermediate'
                    elif randint(1, 4) <= 3:  # 30%
                        profile.tech_level = 'Expert'
                    else:  # 10%
                        profile.tech_level = 'Geek'

                # if we give each influence a 10% chance,
                # we have a total chance of 50% users with at least one influence
                # p = 1 - NthRoot(q) with q = 50%, N = len(INFLUENCES) = 7
                for influence in INFLUENCES:
                    if randint(1, 10) == 1:
                        Influence.objects.create(user=profile.user, influence=influence[0])

                for d in DEVICES:
                    device = d[0]
                    if device == 'Wearable':
                        lim = 20
                    else:
                        lim = 5
                    if randint(1, lim) == 1:
                        DeviceUsage.objects.create(user=profile.user, device=device)

                for p in PLATFORMS:
                    platform = p[0]
                    if platform == 'Linux':
                        lim = 5
                    elif platform == 'OS X':
                        lim = 10
                    elif platform == 'MS Windows':
                        lim = 80
                    elif platform == 'Android':
                        lim = 40
                    elif platform == 'iOS':
                        lim = 10
                    else:
                        lim = 0
                    if randint(1, 100) <= lim:
                        PlatformUsage.objects.create(user=profile.user, platform=platform)

                # one in three has synced data
                if randint(1, 3) == 1:
                    my_activities = []
                    n_of_different_activities = randint(2, 20)
                    for _ in range(0, n_of_different_activities):
                        # find a new, random activity
                        activity = None
                        while True:
                            activity = activities[randint(1, len(activities)) - 1]
                            if activity not in my_activities:
                                my_activities.append(activity)
                                break

                        # instances
                        n_of_instances = randint(1, 20)
                        for __ in range(0, n_of_instances):
                            start_at = get_random_date()
                            end_at = start_at + timedelta(hours=randint(0, 2), minutes=randint(5, 50))
                            Performs.objects.create(user=profile.user, activity=activity,
                                                    start_date=start_at, end_date=end_at)
                # show processed profile
                print(profile.user.username)

                # save changes
                profile.user.save()
                profile.save()
        print('Done')
