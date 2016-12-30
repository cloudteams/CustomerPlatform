# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0025_auto_20161230_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='dismissed',
            field=models.BooleanField(default=False),
        ),
    ]
