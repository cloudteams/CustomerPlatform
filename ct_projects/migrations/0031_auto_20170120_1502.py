# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0030_auto_20170118_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='answer_value',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='max_answers',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='manager',
            field=models.ForeignKey(default=None, blank=True, to='ct_projects.ProjectManager', null=True),
        ),
    ]
