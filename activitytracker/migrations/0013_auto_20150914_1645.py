# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('activitytracker', '0012_auto_20150911_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserUniqueTokens',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=50)),
                ('token_type', models.CharField(max_length=50)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='userverification',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserVerification',
        ),
    ]
