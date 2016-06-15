# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-10 22:31
from __future__ import unicode_literals

from django.db import migrations


def migrate_reserved_blocks(apps, schema_editor):
    Block = apps.get_model('hosts', 'ReservedAddressBlock')
    NetBlock = apps.get_model('networks', 'ReservedAddressBlock')
    Network = apps.get_model('networks', 'Network')

    for block in Block.objects.all():
        new_net = Network.objects.get(id=block.network.id)
        new_block = NetBlock(id=block.id, network=new_net, start_address=block.start_address,
                             end_address=block.end_address, description=block.description)
        new_block.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0020_auto_20160610_1514'),
    ]

    operations = [
        migrations.RunPython(migrate_reserved_blocks)
    ]