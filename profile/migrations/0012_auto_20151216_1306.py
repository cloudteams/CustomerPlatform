# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profile', '0011_auto_20151216_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='Influence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('influence', models.CharField(max_length=255, choices=[(b'FAMILY', b'Family & relatives'), (b'FRIENDS', b'Friends & social circle'), (b'COWORKERS', b'Co-workers'), (b'ADS', b'Advertisement'), (b'TV', b'TV & Media'), (b'BLOGS', b'Blogs'), (b'OTHER', b'Other')])),
                ('user', models.ForeignKey(related_name='influences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='influences',
            name='user',
        ),
        migrations.DeleteModel(
            name='Influences',
        ),
    ]
