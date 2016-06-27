# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0004_reservedaddressblock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservedaddressblock',
            old_name='start_addresss',
            new_name='start_address',
        ),
    ]
