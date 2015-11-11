# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0006_auto_20151111_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bscwproject',
            name='title',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
