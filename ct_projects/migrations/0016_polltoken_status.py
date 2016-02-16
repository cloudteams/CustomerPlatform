# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0015_auto_20151223_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='polltoken',
            name='status',
            field=models.CharField(default=b'OPEN', max_length=8, choices=[(b'OPEN', b'Not used'), (b'USED', b'Successfully used')]),
        ),
    ]
