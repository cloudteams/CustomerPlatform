# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0019_auto_20150421_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='hasSuperActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subactivity', models.ForeignKey(related_name='subactivity', to='activitytracker.Activity')),
                ('superactivity', models.ForeignKey(related_name='superactivity', to='activitytracker.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='performs',
            name='result',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
    ]
