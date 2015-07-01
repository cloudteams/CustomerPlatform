# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0016_auto_20150418_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='performs',
            name='location_latLng',
        ),
        migrations.RemoveField(
            model_name='places',
            name='place_latLng',
        ),
        migrations.AddField(
            model_name='performs',
            name='location_lat',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='performs',
            name='location_lng',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='places',
            name='place_lat',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='places',
            name='place_lng',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='performs',
            name='friends',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='performs',
            name='location_address',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
    ]
