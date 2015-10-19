# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile_wizard', '0005_auto_20151019_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tech_level',
            field=models.CharField(default=b'', max_length=8, blank=True, choices=[(b'BEG', b'Beginner'), (b'INT', b'Intermediate'), (b'EXP', b'Expert'), (b'GEEK', b'gEEk')]),
        ),
    ]
