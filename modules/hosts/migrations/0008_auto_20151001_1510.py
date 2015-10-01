# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0007_auto_20151001_1106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cluster',
            name='slug',
        ),
        migrations.AddField(
            model_name='cluster',
            name='description',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.SlugField(),
        ),
    ]
