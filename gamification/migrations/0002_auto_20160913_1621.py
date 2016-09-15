# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xprule',
            name='event',
            field=models.CharField(max_length=255, choices=[(b'SIGNUP', b'Complete Signup'), (b'PROFILE_COMPLETE', b'Complete Profile 100%'), (b'CONNECT_SERVICE', b'Connect a new connected service'), (b'DISCONNECT_SERVICE', b'Disconnect a connected service'), (b'NEW_IDEA', b'Propose a new idea'), (b'PROJECT_FOLLOW', b'Follow a project'), (b'INVITATION_ACCEPTED', b'Invite a friend who joins the CloudTeams platform'), (b'CAMPAIGN_RESPONSE', b'Participate in a project task, complete it'), (b'REDEEM_POINTS', b'Redeem your points on a reward'), (b'OPEN_ACTIVITY_TRACKER', b'Open the Activity Tracker')]),
        ),
    ]
