# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0012_auto_20150416_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performsproviderinfo',
            name='provider_instance_id',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
