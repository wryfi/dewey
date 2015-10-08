# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0009_auto_20151003_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostrole',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='hostrole',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
