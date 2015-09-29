from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_enumfield import enum
from django.contrib.contenttypes import generic
from django.db import models

from . import RackOrientation, SwitchInterconnect, SwitchSpeed


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
    slug  = models.SlugField()
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
        return '{}: {}'.format(self.cabinet.slug, self.equipment.model)


class AssetBase(models.Model):
    ephor_id = models.PositiveIntegerField(unique=True)
    asset_tag = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    serial = models.CharField(max_length=256, blank=True)
    rack_units = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class Server(AssetBase):
    connected_to = generic.GenericRelation(
        'PortAssignment',
        content_type_field='connected_device_type',
        object_id_field='connected_device_id'
    )

    def __str__(self):
        return 'server #{}'.format(self.asset_tag)


class PowerDistributionUnit(AssetBase):
    volts = models.PositiveIntegerField()
    amps = models.PositiveIntegerField()
    ports = models.PositiveIntegerField()
    connected_devices = generic.GenericRelation(
        'PortAssignment',
        content_type_field='device_type',
        object_id_field='device_id'
    )


class NetworkSwitch(AssetBase):
    speed = enum.EnumField(SwitchSpeed)
    interconnect = enum.EnumField(SwitchInterconnect)
    connected_devices = generic.GenericRelation(
        'PortAssignment',
        content_type_field='device_type',
        object_id_field='device_id'
    )


class PortAssignment(models.Model):
    device_type = models.ForeignKey('ContentType')
    device_id = models.PositiveIntegerField()
    device = GenericForeignKey('device_type', 'device_id')
    port = models.PositiveIntegerField()
    connected_device_type = models.ForeignKey('ContentType')
    connected_device_id = models.PositiveIntegerField()
    connected_device = GenericForeignKey('connected_device_type', 'connected_device_id')