# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profile', '0009_auto_20151110_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device', models.CharField(max_length=255, choices=[(b'PC', b'PC'), (b'LT', b'Laptop'), (b'TB', b'Tablet'), (b'MF', b'Mobile phone'), (b'WE', b'Wearable')])),
                ('user', models.ForeignKey(related_name='devices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Influences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('influence', models.CharField(max_length=255, choices=[(b'PC', b'PC'), (b'LT', b'Laptop'), (b'TB', b'Tablet'), (b'MF', b'Mobile phone'), (b'WE', b'Wearable')])),
                ('user', models.ForeignKey(related_name='influences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlatformUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=255, choices=[(b'MSWIN', b'MS Windows'), (b'OSX', b'OS X'), (b'LINUX', b'Linux'), (b'IOS', b'iOS'), (b'ANDR', b'Android')])),
                ('user', models.ForeignKey(related_name='platforms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='devices',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='influences',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='platforms',
        ),
    ]
