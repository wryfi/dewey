# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0002_remove_host_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='operating_system',
            field=models.IntegerField(default=1),
        ),
    ]
