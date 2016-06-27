# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0011_auto_20151013_1031'),
    ]

    operations = [
        migrations.RenameField(
            model_name='network',
            old_name='network',
            new_name='cidr',
        ),
        migrations.AlterUniqueTogether(
            name='addressassignment',
            unique_together=set([('network', 'address')]),
        ),
    ]
