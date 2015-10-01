# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0006_auto_20151001_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostrole',
            name='name',
            field=models.SlugField(unique=True),
        ),
    ]
