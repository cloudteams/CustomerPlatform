# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0005_auto_20150409_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userverification',
            name='verification_code',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
