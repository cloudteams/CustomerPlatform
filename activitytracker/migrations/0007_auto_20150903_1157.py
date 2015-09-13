# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0006_routine_day_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routine',
            name='day_type',
            field=models.CharField(default=b'Weekdays', max_length=8, choices=[(b'Weekdays', b'Weekdays'), (b'Weekend', b'Weekend')]),
        ),
    ]
