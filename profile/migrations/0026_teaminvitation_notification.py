# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0042_auto_20170206_1428'),
        ('profile', '0025_auto_20170208_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='teaminvitation',
            name='notification',
            field=models.ForeignKey(default=None, blank=True, to='ct_projects.Notification', null=True),
        ),
    ]
