# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('hardware', '0003_server_rack_units'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('position', models.PositiveIntegerField(null=True, blank=True)),
                ('orientation', models.IntegerField(null=True, blank=True, default=1)),
                ('equipment_id', models.PositiveIntegerField()),
                ('cabinet', models.ForeignKey(to='hardware.Cabinet')),
                ('equipment_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkSwitch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('ephor_id', models.PositiveIntegerField(unique=True)),
                ('asset_tag', models.CharField(max_length=128)),
                ('manufacturer', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
                ('serial', models.CharField(max_length=256, blank=True)),
                ('rack_units', models.IntegerField(null=True, blank=True)),
                ('speed', models.IntegerField(default=1)),
                ('interconnect', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PortAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('device_id', models.PositiveIntegerField()),
                ('port', models.PositiveIntegerField()),
                ('connected_device_id', models.PositiveIntegerField()),
                ('connected_device_type', models.ForeignKey(related_name='connected_device', to='contenttypes.ContentType')),
                ('device_type', models.ForeignKey(related_name='port_assignment', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='PowerDistributionUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('ephor_id', models.PositiveIntegerField(unique=True)),
                ('asset_tag', models.CharField(max_length=128)),
                ('manufacturer', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
                ('serial', models.CharField(max_length=256, blank=True)),
                ('rack_units', models.IntegerField(null=True, blank=True)),
                ('volts', models.PositiveIntegerField()),
                ('amps', models.PositiveIntegerField()),
                ('ports', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='server',
            name='cabinet',
        ),
        migrations.RemoveField(
            model_name='server',
            name='orientation',
        ),
        migrations.RemoveField(
            model_name='server',
            name='position',
        ),
        migrations.AlterField(
            model_name='server',
            name='ephor_id',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
