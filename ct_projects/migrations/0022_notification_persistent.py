# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0021_notification_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='persistent',
            field=models.BooleanField(default=True),
        ),
    ]
