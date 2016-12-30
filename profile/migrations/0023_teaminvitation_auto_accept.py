# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0022_teaminvitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='teaminvitation',
            name='auto_accept',
            field=models.BooleanField(default=False),
        ),
    ]
