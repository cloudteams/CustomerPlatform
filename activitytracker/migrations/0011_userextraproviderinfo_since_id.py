# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0010_userextraproviderinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextraproviderinfo',
            name='since_id',
            field=models.BigIntegerField(default=0),
        ),
    ]
