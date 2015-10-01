# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0005_auto_20150930_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostrole',
            name='slug',
        ),
        migrations.AddField(
            model_name='hostrole',
            name='description',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='hostrole',
            name='name',
            field=models.SlugField(),
        ),
    ]
