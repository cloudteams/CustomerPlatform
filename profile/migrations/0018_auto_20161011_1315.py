# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0017_platforminvitation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='education',
            field=models.CharField(default=b'', max_length=127, blank=True, choices=[(b'Elementary', b'Elementary'), (b'Secondary', b'Secondary'), (b'Tertiary', b'Tertiary'), (b'I prefer not to say', b'I prefer not to say')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='employment_status',
            field=models.CharField(default=b'', max_length=127, blank=True, choices=[(b'Student', b'Student'), (b'Unemployed', b'Unemployed'), (b'Employed', b'Employed'), (b'Self-employed', b'Self-employed'), (b'Pensioner', b'Pensioner'), (b'I prefer not to say', b'I prefer not to say')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='tech_level',
            field=models.CharField(default=b'', max_length=31, blank=True, choices=[(b'Beginner', b'Newbie'), (b'Intermediate', b'Intermediate'), (b'Expert', b'Skilled'), (b'Geek', b'Expert')]),
        ),
    ]
