# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0029_notificationemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='trend_factor',
            field=models.FloatField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='project',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
