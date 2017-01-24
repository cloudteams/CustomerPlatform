# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0031_auto_20170120_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]
