# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0004_auto_20150929_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkswitch',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='networkswitch',
            name='name',
            field=models.SlugField(default='switch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='powerdistributionunit',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='powerdistributionunit',
            name='name',
            field=models.SlugField(default='pdu'),
            preserve_default=False,
        ),
    ]
