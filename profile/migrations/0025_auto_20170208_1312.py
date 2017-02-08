# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0024_userprofile_email_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='year_of_birth',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
    ]
