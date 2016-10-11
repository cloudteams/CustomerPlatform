# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0016_platforminvitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='platforminvitation',
            name='status',
            field=models.CharField(default=b'PENDING', max_length=15, choices=[(b'PENDING', b'Pending'), (b'ACCEPTED', b'Accepted')]),
        ),
    ]
