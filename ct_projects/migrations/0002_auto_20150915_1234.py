# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectfollowing',
            old_name='project',
            new_name='project_pk',
        ),
        migrations.AddField(
            model_name='projectfollowing',
            name='created',
            field=models.DateTimeField(default=None, auto_now_add=True),
            preserve_default=False,
        ),
    ]
