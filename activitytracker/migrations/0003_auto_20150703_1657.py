# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0002_auto_20150703_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performsproviderinfo',
            name='provider_instance_url',
            field=models.URLField(null=True),
        ),
    ]
