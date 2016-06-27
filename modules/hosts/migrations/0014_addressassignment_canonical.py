# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0013_auto_20151110_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressassignment',
            name='canonical',
            field=models.BooleanField(help_text='This address is the canonical (DNS) address for the host', default=True),
        ),
    ]
