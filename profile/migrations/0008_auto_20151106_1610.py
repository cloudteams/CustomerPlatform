# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0007_auto_20151019_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='has_been_saved',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(default=None, null=True, upload_to=b'media/avatars/', blank=True),
        ),
    ]
