from django.db import models


class ServerRole(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=128)

    def __str__(self):
        return 'role: {}'.format(self.name)


class Host(models.Model):
    hostname = models.CharField(max_length=256)
    roles = models.ManyToManyField('ServerRole')

    @property
    def domain(self):
        components = hostname.split('.')
        domain = components[1:]
        return '.'.join(domain)

    def __str__(self):
        return self.hostname


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


