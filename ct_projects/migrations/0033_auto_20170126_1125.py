# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0032_campaign_closed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('image_link', models.CharField(default=b'', max_length=1024)),
                ('download_ref', models.CharField(default=b'', max_length=1024)),
                ('name', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('cost', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('total_amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('given', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('remaining', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='rewards',
        ),
        migrations.RemoveField(
            model_name='project',
            name='rewards',
        ),
        migrations.AddField(
            model_name='reward',
            name='project',
            field=models.ForeignKey(related_name='rewards', to='ct_projects.Project'),
        ),
    ]
