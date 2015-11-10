# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0006_auto_20151019_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbrandopinion',
            name='brand',
            field=models.CharField(max_length=16),
        ),
    ]
