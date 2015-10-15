# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0003_idea_idearating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idearating',
            name='idea',
            field=models.ForeignKey(related_name='ratings', to='ct_projects.Idea'),
        ),
    ]
