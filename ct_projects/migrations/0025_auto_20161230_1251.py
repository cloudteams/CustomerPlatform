# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0024_project_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='custom_action',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='notification',
            name='custom_action_text',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='notification',
            name='dismiss_action',
            field=models.TextField(default=b''),
        ),
    ]
