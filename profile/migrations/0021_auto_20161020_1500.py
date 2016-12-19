# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0020_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tech_level',
            field=models.CharField(default=b'', max_length=31, blank=True, choices=[(b'Beginner', b'Newbie'), (b'Intermediate', b'Intermediate'), (b'Expert', b'Skilled'), (b'Geek', b'Expert')]),
        ),
    ]
