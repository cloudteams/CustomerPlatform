# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0013_auto_20151223_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='expires',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
