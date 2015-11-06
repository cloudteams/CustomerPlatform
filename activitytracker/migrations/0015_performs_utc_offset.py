# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0014_auto_20150915_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='performs',
            name='utc_offset',
            field=models.IntegerField(default=0),
        ),
    ]
