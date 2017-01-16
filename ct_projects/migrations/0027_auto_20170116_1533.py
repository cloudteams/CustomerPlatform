# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ct_projects', '0026_notification_dismissed'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('image_link', models.CharField(default=b'', max_length=1024)),
                ('author', models.CharField(default=b'', max_length=1024)),
                ('content', models.TextField()),
                ('project', models.ForeignKey(related_name='blogs', to='ct_projects.Project')),
            ],
        ),
        migrations.AlterModelOptions(
            name='idea',
            options={'ordering': ['-created']},
        ),
    ]
