# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import profile.multiple_choice_field


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0008_auto_20151106_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='devices',
            field=profile.multiple_choice_field.MultiSelectField(default=b'', max_length=255, blank=True, choices=[(b'PC', b'PC'), (b'LT', b'Laptop'), (b'TB', b'Tablet'), (b'MF', b'Mobile phone'), (b'WE', b'Wearable')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='influences',
            field=profile.multiple_choice_field.MultiSelectField(default=b'', max_length=255, blank=True, choices=[(b'FAMILY', b'Family & relatives'), (b'FRIENDS', b'Friends & social circle'), (b'COWORKERS', b'Co-workers'), (b'ADS', b'Advertisement'), (b'TV', b'TV & Media'), (b'BLOGS', b'Blogs'), (b'OTHER', b'Other')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='platforms',
            field=profile.multiple_choice_field.MultiSelectField(default=b'', max_length=255, blank=True, choices=[(b'MSWIN', b'MS Windows'), (b'OSX', b'OS X'), (b'LINUX', b'Linux'), (b'IOS', b'iOS'), (b'ANDR', b'Android')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(default=None, null=True, upload_to=b'avatars/', blank=True),
        ),
    ]
