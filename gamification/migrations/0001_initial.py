# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GamificationProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('xp_points', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='XPRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.CharField(max_length=255, choices=[(b'SIGNUP', b'Complete Signup'), (b'PROFILE_COMPLETE', b'Complete Profile 100%'), (b'CONNECT_SERVICE', b'Connect a new connected service'), (b'DISCONNECT_SERVICE', b'Disconnect a connected service'), (b'NEW_IDEA', b'Propose a new idea'), (b'PROJECT_FOLLOW', b'Follow a project'), (b'PROJECT_FOLLOW', b'Follow a project'), (b'INVITATION_ACCEPTED', b'Invite a friend who joins the CloudTeams platform'), (b'CAMPAIGN_RESPONSE', b'Participate in a project task, complete it'), (b'REDEEM_POINTS', b'Redeem your points on a reward'), (b'OPEN_ACTIVITY_TRACKER', b'Open the Activity Tracker')])),
                ('recurring', models.BooleanField(default=True)),
                ('reward', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='XPRuleApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('rule', models.ForeignKey(to='gamification.XPRule')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
