# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.timezone import now


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ct_projects', '0012_auto_20151214_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('link', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PollToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token_link', models.URLField()),
                ('persona_id', models.IntegerField()),
                ('poll', models.ForeignKey(related_name='tokens', to='ct_projects.Poll')),
                ('user', models.ForeignKey(related_name='poll_tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='campaign',
            old_name='title',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_type',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='content_url',
        ),
        migrations.AddField(
            model_name='campaign',
            name='starts',
            field=models.DateTimeField(default=now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='campaign',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='managers',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='campaign',
            field=models.ForeignKey(related_name='polls', to='ct_projects.Campaign'),
        ),
        migrations.AddField(
            model_name='document',
            name='campaign',
            field=models.ForeignKey(related_name='documents', to='ct_projects.Campaign'),
        ),
    ]
