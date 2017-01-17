# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0028_auto_20170116_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(related_name='emails', to='ct_projects.Notification')),
            ],
        ),
    ]
