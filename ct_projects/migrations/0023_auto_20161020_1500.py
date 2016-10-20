# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0022_notification_persistent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polltoken',
            name='status',
            field=models.CharField(default=b'OPEN', max_length=8, choices=[(b'OPEN', b'Not used'), (b'USED', b'Used to retrieve document'), (b'DONE', b'Used to retrieve & complete document')]),
        ),
    ]
