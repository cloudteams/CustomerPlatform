# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0011_auto_20151214_1625'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectfollowing',
            name='project_pk',
        ),
        migrations.AddField(
            model_name='projectfollowing',
            name='project',
            field=models.ForeignKey(related_name='followed', default=None, to='ct_projects.Project'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projectfollowing',
            name='user',
            field=models.ForeignKey(related_name='follows', to=settings.AUTH_USER_MODEL),
        ),
    ]
