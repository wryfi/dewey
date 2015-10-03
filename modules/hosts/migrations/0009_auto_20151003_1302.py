# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0008_auto_20151001_1510'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cluster',
            old_name='hosts',
            new_name='members',
        ),
        migrations.AddField(
            model_name='reservedaddressblock',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
