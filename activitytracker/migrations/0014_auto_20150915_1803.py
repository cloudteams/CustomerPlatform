# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0013_auto_20150914_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='seasonal_end',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='routine',
            name='seasonal_start',
            field=models.DateField(null=True),
        ),
    ]
