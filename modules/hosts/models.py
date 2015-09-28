from django_enumfield import enum

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
        components = hostname.split('.')
        domain = components[1:]
        return '.'.join(domain)

    def __str__(self):
        return self.hostname


class Cluster(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    kind = enum.EnumField(ClusterType)
    hosts = models.ManyToManyField('Host')


class Network(models.Model):
    slug = models.SlugField()
    network = models.CharField(max_length=18, help_text='CIDR notation')
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.slug

    @property
    def range(self):
        return iptools.IpRange(self.cidr)

    @property
    def unused_addresses(self):
        available = []
        assigned = self.addressassignment_set.all()
        return [addr for addr in self.range if addr not in self.addressassignment_set.all()]

    def get_unused_address(self):
        return self.unused_addresses[0]


class AddressAssignment(models.Model):
    network = models.ForeignKey('Network')
    address = models.CharField(max_length=15)
    host = models.ForeignKey('Host')

    def __str__(self):
        return self.address