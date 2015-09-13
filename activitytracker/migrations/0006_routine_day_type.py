# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0005_routine'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='day_type',
            field=models.CharField(default=b'WD', max_length=2, choices=[(b'WD', b'Weekdays'), (b'WE', b'Weekend')]),
        ),
    ]
