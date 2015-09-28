# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0002_auto_20150924_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='rack_units',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
