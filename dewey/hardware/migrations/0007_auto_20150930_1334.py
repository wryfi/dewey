# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0006_auto_20150930_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('ephor_id', models.PositiveIntegerField(unique=True)),
                ('asset_tag', models.CharField(max_length=128)),
                ('manufacturer', models.CharField(blank=True, max_length=128)),
                ('model', models.CharField(blank=True, max_length=128)),
                ('serial', models.CharField(blank=True, max_length=256)),
                ('rack_units', models.IntegerField(blank=True, null=True)),
                ('name', models.SlugField()),
                ('description', models.CharField(max_length=256)),
                ('ports', models.PositiveIntegerField()),
                ('speed', models.IntegerField(default=1)),
                ('interconnect', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='NetworkSwitch',
        ),
    ]
