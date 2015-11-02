# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0004_auto_20151009_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orig_pk', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('publisher', models.CharField(max_length=256)),
            ],
        ),
    ]
