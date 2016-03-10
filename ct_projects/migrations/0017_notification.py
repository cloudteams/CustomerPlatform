# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ct_projects', '0016_polltoken_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seen', models.BooleanField(default=False)),
                ('document', models.ForeignKey(default=None, blank=True, to='ct_projects.Document')),
                ('poll', models.ForeignKey(default=None, blank=True, to='ct_projects.Poll')),
                ('user', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
