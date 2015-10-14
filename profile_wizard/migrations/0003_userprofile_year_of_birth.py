# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('profile_wizard', '0002_userprofile_years_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='year_of_birth',
            field=models.IntegerField(default=None, null=True, blank=True, validators=[django.core.validators.MinValueValidator(1930), django.core.validators.MaxValueValidator(2010)]),
        ),
    ]
