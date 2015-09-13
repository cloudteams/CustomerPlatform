# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0011_userextraproviderinfo_since_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userextraproviderinfo',
            name='since_id',
            field=models.CharField(default=b'0', max_length=50),
        ),
    ]
