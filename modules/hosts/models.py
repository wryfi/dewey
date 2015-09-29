from django_enumfield import enum
import iptools
import os
import random
import subprocess

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from . import HostType, ClusterType


class HostRole(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=128)

    def __str__(self):
        return 'role: {}'.format(self.name)


class Host(models.Model):
    hostname = models.CharField(max_length=256, help_text='FQDN')
    kind = enum.EnumField(HostType)
    roles = models.ManyToManyField('HostRole', blank=True)
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    parent = GenericForeignKey('parent_type', 'parent_id')

    @property
    def domain(self):
        components = self.hostname.split('.')
        domain = components[1:]
        return '.'.join(domain)

    @property
    def shortname(self):
        return self.hostname.split('.')[0]

    def __str__(self):
        return self.hostname


class Cluster(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    kind = enum.EnumField(ClusterType)
    hosts = models.ManyToManyField('Host')

    def __str__(self):
        return 'cluster: {}'.format(self.slug)


class Network(models.Model):
    slug = models.SlugField()
    network = models.CharField(max_length=18, help_text='CIDR notation')
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.slug

    @property
    def range(self):
        return iptools.IpRange(self.network)

    @property
    def unused_addresses(self):
        available = []
        assigned = [assign.address for assign in self.addressassignment_set.all()]
        for address in self.range:
            if address not in assigned:
                if address != self.range[0] and address != self.range[-1]:
                    available.append(address)
        return available

    def get_unused_address(self):
        random_ip = random.choice(self.unused_addresses)
        try:
            with open(os.devnull, 'w') as nullfile:
                subprocess.check_call(['ping', '-c', '1', '-w', '1', random_ip], stdout=nullfile, stderr=nullfile)
            return random_ip
        except subprocess.CalledProcessError:
            return self.get_unused_address()


class AddressAssignment(models.Model):
    network = models.ForeignKey('Network')
    address = models.CharField(max_length=15)
    host = models.ForeignKey('Host')

    def __str__(self):
        return self.address