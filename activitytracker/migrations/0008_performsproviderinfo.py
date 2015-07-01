# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0007_auto_20150409_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformsProviderInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(max_length=100)),
                ('instance', models.OneToOneField(to='activitytracker.Performs')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
