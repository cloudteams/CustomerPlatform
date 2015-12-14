# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0008_merge'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectInfo',
        ),
        migrations.RemoveField(
            model_name='bscwproject',
            name='id',
        ),
        migrations.RemoveField(
            model_name='bscwproject',
            name='owner_username',
        ),
        migrations.RemoveField(
            model_name='bscwproject',
            name='team_name',
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='application_type',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='bscw_id',
            field=models.IntegerField(default=None, serialize=False, primary_key=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='category',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='project_manager',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='project_members',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bscwproject',
            name='rewards',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bscwproject',
            name='description',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bscwproject',
            name='title',
            field=models.TextField(max_length=255),
        ),
    ]
