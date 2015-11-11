# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0012_auto_20151109_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='interface_id',
            field=models.PositiveIntegerField(default=0, help_text='what interface should minions associate this addr with?'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='network',
            name='cidr',
            field=models.CharField(max_length=18, help_text='network CIDR notation, e.g. 192.168.1.0/24'),
        ),
    ]
