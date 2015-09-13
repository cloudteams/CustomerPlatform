# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default', '0003_alter_email_max_length'),
        ('activitytracker', '0009_user_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExtraProviderInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_updated', models.CharField(default=b'0000-00-00 00:00:00', max_length=20)),
                ('social_instance', models.OneToOneField(to='default.UserSocialAuth')),
            ],
        ),
    ]
