# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0020_notification_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 18, 15, 16, 31, 573000), auto_now_add=True),
            preserve_default=False,
        ),
    ]
