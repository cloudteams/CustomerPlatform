# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0042_auto_20170206_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='contacts',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
