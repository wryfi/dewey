from django_enumfield import enum
import iptools
import os
import subprocess

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from . import ClusterType, OperatingSystem


class HostRole(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Host(models.Model):
    """
    A network host. Hosts must have a parent, which may be: (1) a piece of hardware
    (e.g. Server, PowerDistributionUnit, or NetworkDevice); or (2) another host
    (e.g. for a static VM); or (3) a cluster of hosts (e.g. a VM on an ESXi cluster)
    """
    hostname = models.CharField(max_length=256, help_text='FQDN')
    roles = models.ManyToManyField('HostRole', blank=True)
    operating_system = enum.EnumField(OperatingSystem)
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    parent = GenericForeignKey('parent_type', 'parent_id')

    def __str__(self):
        return self.hostname

    @property
    def domain(self):
        components = self.hostname.split('.')
        domain = components[1:]
        return '.'.join(domain)

    @property
    def kind(self):
        # can't be imported with module - creates circular import
        from hardware.models import Server
        if type(self.parent) == Host or type(self.parent) == Cluster:
            return 'virtual machine host'
        elif type(self.parent) == Server:
            return 'bare metal host'
        else:
            return 'peripheral host'

    @property
    def shortname(self):
        return self.hostname.split('.')[0]


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

    def address_allocated(self, address):
        if address in self.reserved_addresses:
            return True
        if address in self.unused_addresses:
            return False
        else:
            return True

    def get_unused_address(self, index=0):
        try:
            next_ip = self.unused_addresses[index]
            with open(os.devnull, 'w') as nullfile:
                subprocess.check_call(['ping', '-c', '1', '-w', '1', next_ip],
                                      stdout=nullfile, stderr=nullfile)
            return next_ip
        except IndexError:
            return 0
        except subprocess.CalledProcessError:
            return self.get_unused_address(index+1)

    @property
    def range(self):
        return iptools.IpRange(self.network)

    @property
    def reserved_addresses(self):
        """
        Unfortunately, there's no built-in way to concatenate IpRange objects,
        so to get a comprehensive list of addresses in reserved blocks, we have
        to construct it manually.
        """
        reserved = []
        for block in self.reservedaddressblock_set.all():
            for address in block.range:
                reserved.append(address)
        return reserved

    @property
    def unused_addresses(self):
        available = []
        assigned = [assign.address for assign in self.addressassignment_set.all()]
        for address in self.range:
            if address not in assigned:
                if address != self.range[0] and address != self.range[-1]:
                    if address not in self.reserved_addresses:
                        available.append(address)
        return available


class AddressAssignment(models.Model):
    network = models.ForeignKey('Network')
    address = models.CharField(max_length=15)
    host = models.ForeignKey('Host')

    def __str__(self):
        return self.address


class ReservedAddressBlock(models.Model):
    network = models.ForeignKey('Network')
    start_address = models.GenericIPAddressField()
    end_address = models.GenericIPAddressField()

    def __str__(self):
        return 'Reserved addresses: {} - {}'.format(self.start_address, self.end_address)

    @property
    def range(self):
        return iptools.IpRange(self.start_address, self.end_address)