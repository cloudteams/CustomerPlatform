# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0010_remove_performsproviderinfo_provider_instance_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='performsproviderinfo',
            name='provider_instance_id',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
