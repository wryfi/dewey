from django_enumfield import enum
from django.db import models

from . import RackOrientation


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
        return 'cabinet: {}'.format(self.name)


class Server(models.Model):
    ephor_id = models.IntegerField(unique=True)
    asset_tag = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    serial = models.CharField(max_length=256, blank=True)
    cabinet = models.ForeignKey('Cabinet', blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    rack_units = models.IntegerField(blank=True, null=True)
    orientation = enum.EnumField(RackOrientation, blank=True, null=True)

    def __str__(self):
        return 'Asset #{}'.format(self.asset_tag)
