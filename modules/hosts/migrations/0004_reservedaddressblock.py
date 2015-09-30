# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0003_host_operating_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservedAddressBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('start_addresss', models.GenericIPAddressField()),
                ('end_address', models.GenericIPAddressField()),
                ('network', models.ForeignKey(to='hosts.Network')),
            ],
        ),
    ]
