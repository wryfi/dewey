# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0010_auto_20151008_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
