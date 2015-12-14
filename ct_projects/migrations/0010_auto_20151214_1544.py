# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0009_auto_20151214_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('expires', models.DateTimeField()),
                ('rewards', models.TextField(default=None, null=True, blank=True)),
                ('logo', models.URLField(default=None, null=True, blank=True)),
                ('campaign_type', models.CharField(default=b'Questionnaire', max_length=31)),
                ('content_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('project_managers', models.TextField()),
                ('project_members', models.TextField(default=None, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('logo', models.URLField(default=None, null=True, blank=True)),
                ('category', models.TextField(default=None, null=True, blank=True)),
                ('application_type', models.TextField(default=None, null=True, blank=True)),
                ('rewards', models.TextField(default=None, null=True, blank=True)),
                ('is_public', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='BSCWProject',
        ),
        migrations.RemoveField(
            model_name='idea',
            name='project_pk',
        ),
        migrations.AddField(
            model_name='campaign',
            name='project',
            field=models.ForeignKey(related_name='campaigns', to='ct_projects.Project'),
        ),
        migrations.AddField(
            model_name='idea',
            name='project',
            field=models.ForeignKey(related_name='ideas', default=None, to='ct_projects.Project'),
            preserve_default=False,
        ),
    ]
