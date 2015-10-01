from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_enumfield import enum
from django.contrib.contenttypes import generic
from django.db import models

from . import RackOrientation, SwitchInterconnect, SwitchSpeed
from hosts.models import Host


class Datacenter(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    vendor = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    noc_phone = models.CharField(max_length=24, blank=True)
    noc_email = models.EmailField(blank=True)

    def __str__(self):
       return 'datacenter: {}'.format(self.name)


class Cabinet(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    datacenter = models.ForeignKey('Datacenter')
    rack_units = models.IntegerField()

    def __str__(self):
        return 'cabinet: {}'.format(self.slug)


class CabinetAssignment(models.Model):
    cabinet = models.ForeignKey('Cabinet')
    position = models.PositiveIntegerField(blank=True, null=True)
    orientation = enum.EnumField(RackOrientation, blank=True, null=True)
    equipment_type = models.ForeignKey(ContentType)
    equipment_id = models.PositiveIntegerField()
    equipment = GenericForeignKey('equipment_type', 'equipment_id')

    def __str__(self):
        return '{}: {} in position {}'.format(
            self.cabinet.slug,
            self.equipment.model,
            self.position
        )


class AssetBase(models.Model):
    ephor_id = models.PositiveIntegerField(unique=True)
    asset_tag = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    serial = models.CharField(max_length=256, blank=True)
    rack_units = models.IntegerField(blank=True, null=True)
    cabinets = generic.GenericRelation(
        'CabinetAssignment',
        content_type_field='equipment_type',
        object_id_field='equipment_id'
    )
    connected_to = generic.GenericRelation(
        'PortAssignment',
        content_type_field='connected_device_type',
        object_id_field='connected_device_id'
    )
    hosts = generic.GenericRelation(
        Host,
        content_type_field='parent_type',
        object_id_field='parent_id'
    )

    class Meta:
        abstract = True

    def _get_ports(self, cxn_type):
        ports = []
        for connected in self.connected_to.all():
            if type(connected.device) == cxn_type:
                ports.append((connected.device, connected.port))
        return ports

    @property
    def location(self):
        try:
            return (self.cabinets.first().cabinet, self.cabinets.first().position)
        except AttributeError:
            return None

    @property
    def pdu_ports(self):
        return self._get_ports(PowerDistributionUnit)

    @property
    def switch_ports(self):
        return self._get_ports(NetworkDevice)


class Server(AssetBase):
    def __str__(self):
        return 'server #{}'.format(self.asset_tag)


class PeripheralMixin(models.Model):
    name = models.SlugField()
    description = models.CharField(max_length=256)
    ports = models.PositiveIntegerField()
    port_assignments = generic.GenericRelation(
        'PortAssignment',
        content_type_field='device_type',
        object_id_field='device_id'
    )

    class Meta:
        abstract = True

    @property
    def connected_devices(self):
        devices = []
        for assignment in self.port_assignments.all():
            devices.append((assignment.connected_device, assignment.port))
        return devices


class PowerDistributionUnit(PeripheralMixin, AssetBase):
    volts = models.PositiveIntegerField()
    amps = models.PositiveIntegerField()

    def __str__(self):
        return '{}v  {}A pdu'.format(self.volts, self.amps)

    @property
    def watts(self):
        return self.amps * self.volts


class NetworkDevice(PeripheralMixin, AssetBase):
    speed = enum.EnumField(SwitchSpeed)
    interconnect = enum.EnumField(SwitchInterconnect)

    def __str__(self):
        return '{} {} switch'.format(self.get_speed_display(), self.manufacturer)


class PortAssignment(models.Model):
    device_type = models.ForeignKey(ContentType, related_name='port_assignment')
    device_id = models.PositiveIntegerField()
    device = GenericForeignKey('device_type', 'device_id')
    port = models.PositiveIntegerField()
    connected_device_type = models.ForeignKey(ContentType, related_name='connected_device')
    connected_device_id = models.PositiveIntegerField()
    connected_device = GenericForeignKey('connected_device_type', 'connected_device_id')

    def __str__(self):
        return '{} port {}'.format(self.device.name, self.port)
