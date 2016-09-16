# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0005_badge_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
