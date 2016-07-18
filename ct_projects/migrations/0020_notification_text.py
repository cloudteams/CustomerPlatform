# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0019_auto_20160321_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='text',
            field=models.TextField(default=b''),
        ),
    ]
