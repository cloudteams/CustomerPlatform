# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0014_auto_20150416_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performsproviderinfo',
            name='instance',
            field=models.OneToOneField(related_name='instance', to='activitytracker.Performs'),
            preserve_default=True,
        ),
    ]
