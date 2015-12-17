import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import AddressAssignment, Host
from .tasks import create_dns_records, delete_dns_records

logger = logging.getLogger('.'.join(['dewey', __name__]))


@receiver(post_save, sender=AddressAssignment)
def create_dns_records_receiver(sender, **kwargs):
    create_dns_records.delay(kwargs['instance'])


@receiver(pre_delete, sender=AddressAssignment)
def delete_dns_records_receiver(sender, **kwargs):
    delete_dns_records.delay(kwargs['instance'])


@receiver(pre_delete, sender=Host)
def delete_host_address_assignments_receiver(sender, **kwargs):
    host = kwargs['instance']
    for assignment in host.addressassignment_set.all():
        assignment.delete()
