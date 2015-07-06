# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(max_length=2, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('date_of_birth', models.DateField(null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('activity_id', models.AutoField(serialize=False, primary_key=True)),
                ('activity_name', models.CharField(max_length=100)),
                ('description', models.CharField(default=b'', max_length=200)),
                ('icon_classname', models.CharField(default=b'', max_length=50)),
                ('category', models.CharField(max_length=20, null=True, choices=[(b'black', b'Self-care/Everyday Needs'), (b'blue', b'Communication/Socializing'), (b'greenLight', b'Sports/Fitness'), (b'orange', b'Fun/Leisure/Hobbies'), (b'redDark', b'Responsibilities'), (b'purple', b'Transportation')])),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('friends_id', models.AutoField(serialize=False, primary_key=True)),
                ('friend_name', models.CharField(max_length=100)),
                ('friend_of_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='hasSuperActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subactivity', models.ForeignKey(related_name='subactivity', to='activitytracker.Activity')),
                ('superactivity', models.ForeignKey(related_name='superactivity', to='activitytracker.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('object_id', models.AutoField(serialize=False, primary_key=True)),
                ('object_name', models.CharField(max_length=100)),
                ('object_of_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Performs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('goal', models.CharField(max_length=200)),
                ('result', models.CharField(default=b'', max_length=200)),
                ('friends', models.CharField(max_length=200)),
                ('start_date', models.DateTimeField(verbose_name=b'Start Time')),
                ('end_date', models.DateTimeField(verbose_name=b'End Time')),
                ('goal_status', models.CharField(max_length=20, null=True, choices=[(b'Reached', b'Reached'), (b'InProgress', b'In Progress'), (b'Failed', b'Failed')])),
                ('location_address', models.CharField(max_length=200)),
                ('location_lat', models.FloatField(null=True)),
                ('location_lng', models.FloatField(null=True)),
                ('activity', models.ForeignKey(to='activitytracker.Activity', db_column=b'activity_key')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('using', models.ManyToManyField(to='activitytracker.Object')),
            ],
        ),
        migrations.CreateModel(
            name='PerformsProviderInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(max_length=100)),
                ('provider_instance_id', models.CharField(max_length=50)),
                ('performs_provider_url', models.CharField(default=b'33', max_length=200)),
                ('instance', models.OneToOneField(related_name='instance', to='activitytracker.Performs')),
            ],
        ),
        migrations.CreateModel(
            name='Places',
            fields=[
                ('place_id', models.AutoField(serialize=False, primary_key=True)),
                ('place_name', models.CharField(max_length=200)),
                ('place_address', models.CharField(max_length=200)),
                ('place_lat', models.FloatField(null=True)),
                ('place_lng', models.FloatField(null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verification_code', models.CharField(max_length=50)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='places',
            unique_together=set([('user', 'place_name')]),
        ),
    ]
