# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='asset_tag',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='server',
            name='cabinet',
            field=models.ForeignKey(to='hardware.Cabinet', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='ephor_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='orientation',
            field=models.IntegerField(null=True, default=1, blank=True),
        ),
    ]
