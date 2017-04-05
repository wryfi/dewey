# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField()),
                ('rack_units', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Datacenter',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField()),
                ('vendor', models.CharField(max_length=256)),
                ('address', models.CharField(max_length=256)),
                ('noc_phone', models.CharField(max_length=24, blank=True)),
                ('noc_email', models.EmailField(max_length=254, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('ephor_id', models.IntegerField()),
                ('asset_tag', models.IntegerField()),
                ('manufacturer', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
                ('serial', models.CharField(max_length=256, blank=True)),
                ('position', models.IntegerField(null=True, blank=True)),
                ('orientation', models.IntegerField(default=1)),
                ('cabinet', models.ForeignKey(blank=True, to='hardware.Cabinet')),
            ],
        ),
        migrations.AddField(
            model_name='cabinet',
            name='datacenter',
            field=models.ForeignKey(to='hardware.Datacenter'),
        ),
    ]
