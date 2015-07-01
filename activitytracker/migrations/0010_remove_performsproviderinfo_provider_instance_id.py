# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0009_performsproviderinfo_provider_instance_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='performsproviderinfo',
            name='provider_instance_id',
        ),
    ]
