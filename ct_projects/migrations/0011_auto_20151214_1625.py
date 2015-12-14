# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0010_auto_20151214_1544'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_managers',
            new_name='managers',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='project_members',
            new_name='members',
        ),
    ]
