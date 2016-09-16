# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0004_auto_20160916_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='name',
            field=models.CharField(default=b' ', max_length=255),
        ),
    ]
