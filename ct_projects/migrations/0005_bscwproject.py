# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0004_auto_20151009_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='BSCWProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_username', models.CharField(max_length=255)),
                ('team_name', models.CharField(max_length=255)),
                ('created', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('logo', models.URLField(default=None, null=True, blank=True)),
            ],
        ),
    ]
