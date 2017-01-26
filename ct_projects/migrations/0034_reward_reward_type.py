# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0033_auto_20170126_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='reward_type',
            field=models.CharField(default='OTHER', max_length=32, choices=[(b'DOWNLOAD', b'Download'), (b'VOUCHER', b'Voucher'), (b'OTHER', b'Other')]),
            preserve_default=False,
        ),
    ]
