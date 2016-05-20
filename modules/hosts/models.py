from collections import defaultdict
import iptools
import os
import re
import socket
import struct
import subprocess

from django_enumfield import enum
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from . import ClusterType, OperatingSystem


class HostRole(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    # exposing this as a property for generic rest api views
    @property
    def hosts(self):
        return self.host_set.all()


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
    virtual_machines = GenericRelation(
        'Host',
        content_type_field = 'parent_type',
        object_id_field = 'parent_id'
    )

    def __str__(self):
        return self.hostname

    @property
    def domain(self):
        components = self.hostname.split('.')
        return '.'.join(components[1:])

    @property
    def kind(self):
        if not self.parent:
            return 'unknown'
        # can't be imported with module - creates circular import
        from hardware.models import Server
        if type(self.parent) == Host or type(self.parent) == Cluster:
            return 'virtual machine'
        elif type(self.parent) == Server:
            return 'bare metal host os'
        else:
            return 'peripheral host'

    @property
    def shortname(self):
        return self.hostname.split('.')[0]

    @property
    def environment(self):
        match = re.match(r'.*-(\d{3})', self.hostname)
        if match:
            if match.groups()[0][0] == '1':
                return 'prod'
            if match.groups()[0][0] == '2':
                return 'dev'
            if match.groups()[0][0] == '3':
                return 'stage'
            if match.groups()[0][0] == '9':
                return 'vagrant'
        return 'other'

    @property
    def ip_addresses(self):
        grouped = {}
        for assignment in self.address_assignments.all():
            details = {'address': assignment.address, 'network': assignment.network.cidr,
                       'netmask': assignment.network.netmask, 'mask_bits': assignment.network.mask_bits,
                       'gateway': assignment.network.gateway}
            if assignment.network.interface_id not in grouped:
                grouped[assignment.network.interface_id] = [details]
            else:
                grouped[assignment.network.interface_id].append(details)
        return grouped

    @property
    def canonical_assignment(self):
        for assignment in self.address_assignments.all():
            if assignment.canonical:
                return assignment


class Cluster(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=128, blank=True)
    kind = enum.EnumField(ClusterType)
    members = models.ManyToManyField('Host')
    virtual_machines = GenericRelation(
        'Host',
        content_type_field = 'parent_type',
        object_id_field = 'parent_id'
    )

    def __str__(self):
        return 'cluster: {}'.format(self.name)


class Network(models.Model):
    slug = models.SlugField()
    description = models.CharField(max_length=256)
    cidr = models.CharField(max_length=18, help_text='network CIDR notation, e.g. 192.168.1.0/24')
    interface_id = models.PositiveIntegerField(help_text='what interface should minions associate this addr with?')

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
    def mask_bits(self):
        return int(self.cidr.split('/')[1])

    @property
    def netmask(self):
        # I confess I have no idea how this works. See http://goo.gl/WikFMa.
        return socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - self.mask_bits)) & 0xffffffff))

    @property
    def network(self):
        return self.cidr.split('/')[0]

    @property
    def gateway(self):
        return self.range[1]

    @property
    def range(self):
        return iptools.IpRange(self.cidr)

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
    def reverse_zone(self):
        """
        Calculates the name of the reverse DNS zone of the network, by determining the
        significant octets of the IP address, reversing them, and returning a valid in-addr.arpa
        zone name. This works as long as you create your reverse DNS zones based on significant octets.
        """
        # convert ip address into a binary string
        bin_string = ''.join([bin(int(octet)+256)[3:] for octet in self.network.split('.')])
        assert len(bin_string) == 32
        # grab the significant bits from the string
        significant_digits = bin_string[:int(self.mask_bits)]
        # group the significant bits into octets
        significant_by_8 = [significant_digits[i:i+8] for i in range(0, len(significant_digits), 8)]
        significant_octets = []
        # the significant octets, for our purpose, are the ones that have all 8 bits
        for octet in significant_by_8:
            if len(octet) == 8:
                significant_octets.append(str(int(octet, 2)))
        significant_octets.reverse()
        reversed_string = '.'.join(significant_octets)
        return '.'.join([reversed_string, 'in-addr.arpa'])

    @property
    def unused_addresses(self):
        available = []
        assigned = [assign.address for assign in self.address_assignments.all()]
        for address in self.range:
            if address not in assigned:
                if address != self.range[0] and address != self.range[-1]:
                    if address not in self.reserved_addresses:
                        available.append(address)
        return available


class AddressAssignment(models.Model):
    network = models.ForeignKey('Network', related_name='address_assignments')
    address = models.CharField(max_length=15)
    host = models.ForeignKey('Host', related_name='address_assignments')
    canonical = models.BooleanField(default=True, help_text='This address is the canonical (DNS) address for the host')

    class Meta:
        unique_together = (('network', 'address'),)

    def __str__(self):
        if self.canonical:
            return('{} on {}*'.format(self.address, self.host.hostname))
        else:
            return('{} on {}'.format(self.address, self.host.hostname))

    @property
    def ptr_name(self):
        octets = self.address.split('.')
        octets.reverse()
        octets_reversed = '.'.join(octets)
        return '.'.join([octets_reversed, 'in-addr.arpa'])


class ReservedAddressBlock(models.Model):
    network = models.ForeignKey('Network')
    start_address = models.GenericIPAddressField()
    end_address = models.GenericIPAddressField()
    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return 'Reserved addresses: {} - {}'.format(self.start_address, self.end_address)

    @property
    def range(self):
        return iptools.IpRange(self.start_address, self.end_address)
