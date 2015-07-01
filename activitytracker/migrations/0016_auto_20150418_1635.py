# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0015_auto_20150416_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performsproviderinfo',
            name='provider_instance_id',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
