# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0041_auto_20170203_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='answer_value',
            field=models.DecimalField(default=None, null=True, max_digits=8, decimal_places=2, blank=True),
        ),
    ]
