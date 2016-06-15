# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-10 22:14
from __future__ import unicode_literals

from django.db import migrations


def migrate_addr_assignments(apps, schema_editor):
    AddrAssign = apps.get_model('hosts', 'AddressAssignment')
    NetAddrAssign = apps.get_model('networks', 'AddressAssignment')
    Network = apps.get_model('networks', 'Network')
    Host = apps.get_model('environments', 'Host')

    for assign in AddrAssign.objects.all():
        new_net = Network.objects.get(id=assign.network.id)
        new_host = Host.objects.get(id=assign.host.id)
        new_assign = NetAddrAssign(id=assign.id, network=new_net, address=assign.address,
                                   host=new_host, canonical=assign.canonical)
        new_assign.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0019_auto_20160610_1457'),
    ]

    operations = [
        migrations.RunPython(migrate_addr_assignments)
    ]