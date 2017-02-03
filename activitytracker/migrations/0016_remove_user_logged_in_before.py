# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0015_performs_utc_offset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='logged_in_before',
        ),
    ]
