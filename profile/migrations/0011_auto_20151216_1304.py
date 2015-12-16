# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0010_auto_20151216_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='influences',
            name='influence',
            field=models.CharField(max_length=255, choices=[(b'FAMILY', b'Family & relatives'), (b'FRIENDS', b'Friends & social circle'), (b'COWORKERS', b'Co-workers'), (b'ADS', b'Advertisement'), (b'TV', b'TV & Media'), (b'BLOGS', b'Blogs'), (b'OTHER', b'Other')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(default=None, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name_initial',
            field=models.CharField(default=None, max_length=1, null=True, blank=True),
        ),
    ]
