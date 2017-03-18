# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0007_auto_20150930_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='powerdistributionunit',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
