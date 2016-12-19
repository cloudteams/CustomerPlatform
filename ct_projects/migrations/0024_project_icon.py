# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0023_auto_20161020_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='icon',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
