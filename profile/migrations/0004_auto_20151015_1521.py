# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import profile.multiple_choice_field


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_userprofile_year_of_birth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='devices_and_platforms',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='devices',
            field=profile.multiple_choice_field.MultiSelectField(default=b'', max_length=2, blank=True, choices=[(b'PC', b'PC'), (b'LT', b'Laptop computer'), (b'TB', b'Tablet'), (b'MF', b'Mobile phone'), (b'WE', b'Wearable')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='platforms',
            field=profile.multiple_choice_field.MultiSelectField(default=b'', max_length=8, blank=True, choices=[(b'MSWIN', b'Microsoft Windows'), (b'OSX', b'OS X'), (b'LINUX', b'Linux'), (b'iOS', b'iOS'), (b'ANDR', b'Android')]),
        ),
    ]
