# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ct_projects', '0036_auto_20170126_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('provided_info', models.TextField()),
                ('message', models.TextField()),
                ('user', models.ForeignKey(related_name='contact_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
