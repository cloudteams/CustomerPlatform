# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ct_projects', '0034_reward_reward_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardPurchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reward', models.ForeignKey(related_name='sales', to='ct_projects.Reward')),
                ('user', models.ForeignKey(related_name='bought_rewards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
