# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0003_auto_20160915_1600'),
    ]

    operations = [
        migrations.RenameField(
            model_name='badge',
            old_name='title',
            new_name='slogan',
        ),
    ]
