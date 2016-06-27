# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField()),
                ('kind', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(help_text='FQDN', max_length=256)),
                ('kind', models.IntegerField(default=1)),
                ('parent_id', models.PositiveIntegerField()),
                ('parent_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='HostRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('network', models.CharField(help_text='CIDR notation', max_length=18)),
                ('description', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='host',
            name='roles',
            field=models.ManyToManyField(blank=True, to='hosts.HostRole'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='hosts',
            field=models.ManyToManyField(to='hosts.Host'),
        ),
        migrations.AddField(
            model_name='addressassignment',
            name='host',
            field=models.ForeignKey(to='hosts.Host'),
        ),
        migrations.AddField(
            model_name='addressassignment',
            name='network',
            field=models.ForeignKey(to='hosts.Network'),
        ),
    ]
