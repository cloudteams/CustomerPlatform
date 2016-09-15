# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gamification', '0002_auto_20160913_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('rule', models.CharField(max_length=255, choices=[(b'PROJECT_FOLLOW', b'Follow at least -X- project'), (b'CONNECT_SERVICE', b'Connect at least -X- connected services'), (b'INVITATION_ACCEPTED', b'Invite at least -X- friends who join the CloudTeams platform'), (b'NUMBER_OF_PROJECTS_WITH_CONTRIBUTIONS', b'Contribute to at least -X- different projects'), (b'NUMBER_OF_PUBLIC_PROJECTS_WITH_CONTRIBUTIONS', b'Contribute to at least -X- public projects'), (b'PROFILE_COMPLETE', b'Complete Profile')])),
                ('active', models.BooleanField(default=True)),
                ('levels', django.contrib.postgres.fields.ArrayField(base_field=models.SmallIntegerField(), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='BadgeReward',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.SmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(to='gamification.Badge')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='gamificationprofile',
            name='number_of_badges',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='xprule',
            name='event',
            field=models.CharField(max_length=255, choices=[(b'SIGNUP', b'Complete Signup'), (b'PROFILE_COMPLETE', b'Complete Profile'), (b'CONNECT_SERVICE', b'Connect a new connected service'), (b'DISCONNECT_SERVICE', b'Disconnect a connected service'), (b'NEW_IDEA', b'Propose a new idea'), (b'PROJECT_FOLLOW', b'Follow a project'), (b'INVITATION_ACCEPTED', b'Invite a friend who joins the CloudTeams platform'), (b'CAMPAIGN_RESPONSE', b'Participate in a project task, complete it'), (b'REDEEM_POINTS', b'Redeem your points on a reward'), (b'OPEN_ACTIVITY_TRACKER', b'Open the Activity Tracker')]),
        ),
    ]
