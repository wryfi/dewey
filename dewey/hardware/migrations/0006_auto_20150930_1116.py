# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0005_auto_20150930_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkswitch',
            name='ports',
            field=models.PositiveIntegerField(default=48),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='networkswitch',
            name='description',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='powerdistributionunit',
            name='description',
            field=models.CharField(max_length=256),
        ),
    ]
