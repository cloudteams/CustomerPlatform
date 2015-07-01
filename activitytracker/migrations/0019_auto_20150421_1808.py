# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0018_auto_20150421_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performs',
            name='friends',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
    ]
