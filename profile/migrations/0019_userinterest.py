# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profile', '0018_auto_20161011_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInterest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interest', models.CharField(max_length=255, choices=[(b'Business', b'Business'), (b'Education', b'Education'), (b'Entertainment', b'Entertainment'), (b'Finance', b'Finance'), (b'Food & Drinks', b'Food & Drinks'), (b'Health & Fitness', b'Health & Fitness'), (b'Lifestyle', b'Lifestyle'), (b'Medical', b'Medical'), (b'Music', b'Music'), (b'Navigation', b'Navigation'), (b'News', b'News'), (b'Photo & Video', b'Photo & Video'), (b'Productivity', b'Productivity'), (b'Social Networking', b'Social Networking'), (b'Sports', b'Sports'), (b'Travel', b'Travel'), (b'Utilities', b'Utilities'), (b'Weather', b'Weather')])),
                ('user', models.ForeignKey(related_name='interests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
