# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0037_contactrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactrequest',
            name='project',
            field=models.ForeignKey(related_name='contact_requests', default=1, to='ct_projects.Project'),
            preserve_default=False,
        ),
    ]
