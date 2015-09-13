# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0007_auto_20150903_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routine',
            name='end_time',
            field=models.TimeField(null=True, verbose_name=b'End Time'),
        ),
        migrations.AlterField(
            model_name='routine',
            name='start_time',
            field=models.TimeField(null=True, verbose_name=b'Start Time'),
        ),
    ]
