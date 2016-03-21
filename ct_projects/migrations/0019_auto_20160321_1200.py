# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0018_auto_20160310_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='document',
            field=models.ForeignKey(default=None, blank=True, to='ct_projects.Document', null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='poll',
            field=models.ForeignKey(default=None, blank=True, to='ct_projects.Poll', null=True),
        ),
    ]
