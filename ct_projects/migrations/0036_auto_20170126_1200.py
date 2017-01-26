# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0035_rewardpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='rewardpurchase',
            name='coins_spent',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
