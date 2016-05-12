# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-11 21:38
from __future__ import unicode_literals

from django.db import migrations
import django_enumfield.db.fields
import hosts


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0014_addressassignment_canonical'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='kind',
            field=django_enumfield.db.fields.EnumField(default=1, enum=hosts.ClusterType),
        ),
        migrations.AlterField(
            model_name='host',
            name='operating_system',
            field=django_enumfield.db.fields.EnumField(default=1, enum=hosts.OperatingSystem),
        ),
    ]