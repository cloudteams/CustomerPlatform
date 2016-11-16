# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0021_auto_20161020_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_id', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(default=b'PENDING', max_length=15, choices=[(b'PENDING', b'Pending'), (b'ACCEPTED', b'Accepted')])),
            ],
        ),
    ]
