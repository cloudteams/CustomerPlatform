# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0005_bscwproject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bscwproject',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
