# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0023_teaminvitation_auto_accept'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
    ]
