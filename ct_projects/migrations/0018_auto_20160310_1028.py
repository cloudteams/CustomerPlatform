# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0017_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='link',
            field=models.URLField(null=True, blank=True),
        ),
    ]
