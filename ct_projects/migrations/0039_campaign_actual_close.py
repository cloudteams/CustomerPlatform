# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0038_contactrequest_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='actual_close',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
