# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0014_auto_20151223_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polltoken',
            name='persona_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
