# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0008_auto_20151006_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabinet',
            name='posts',
            field=models.PositiveIntegerField(default=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cabinetassignment',
            name='depth',
            field=models.IntegerField(default=1, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='cabinet',
            name='rack_units',
            field=models.PositiveIntegerField(),
        ),
    ]
