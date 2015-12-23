# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0012_auto_20151216_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceusage',
            name='device',
            field=models.CharField(max_length=255, choices=[(b'PC', b'PC'), (b'Laptop', b'Laptop'), (b'Tablet', b'Tablet'), (b'Mobile phone', b'Mobile phone'), (b'Wearable', b'Wearable')]),
        ),
        migrations.AlterField(
            model_name='influence',
            name='influence',
            field=models.CharField(max_length=255, choices=[(b'Family & relatives', b'Family & relatives'), (b'Friends & social circle', b'Friends & social circle'), (b'Co-workers', b'Co-workers'), (b'Advertisement', b'Advertisement'), (b'TV & Media', b'TV & Media'), (b'Blogs', b'Blogs'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='platformusage',
            name='platform',
            field=models.CharField(max_length=255, choices=[(b'MS Windows', b'MS Windows'), (b'OS X', b'OS X'), (b'Linux', b'Linux'), (b'iOS', b'iOS'), (b'Android', b'Android')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='tech_level',
            field=models.CharField(default=b'', max_length=31, blank=True, choices=[(b'Beginner', b'Beginner'), (b'Intermediate', b'Intermediate'), (b'Expert', b'Expert'), (b'Geek', b'gEEk')]),
        ),
    ]
