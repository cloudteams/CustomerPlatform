# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0003_auto_20150703_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='logged_in_before',
            field=models.BooleanField(default=False),
        ),
    ]
