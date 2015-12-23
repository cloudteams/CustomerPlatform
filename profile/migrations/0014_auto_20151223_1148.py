# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0015_auto_20151223_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tech_level',
            field=models.CharField(default=b'', max_length=16, blank=True, choices=[(b'Beginner', b'Beginner'), (b'Intermediate', b'Intermediate'), (b'Expert', b'Expert'), (b'Geek', b'gEEk')]),
        ),
    ]
