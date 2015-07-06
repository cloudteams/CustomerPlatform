# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='performsproviderinfo',
            name='performs_provider_url',
        ),
        migrations.AddField(
            model_name='performsproviderinfo',
            name='provider_instance_url',
            field=models.TextField(null=True),
        ),
    ]
