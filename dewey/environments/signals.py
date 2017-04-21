import logging
import copy
from datetime import timedelta

from celery import chain
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from .models import Host, HostMonitoringException

logger = logging.getLogger('.'.join(['dewey', __name__]))


@receiver(post_save, sender=Host)
def create_monitoring_exception(sender, **kwargs):
    if kwargs.get('created'):
        host = kwargs['instance']
        start = timezone.now()
        end = start + timedelta(seconds=settings.HOST_MONITORING_DELAY)
        HostMonitoringException.objects.create(host=host, start=start, end=end, monitored=False)
        logger.debug('created {}s monitoring exception for {}'.format(settings.HOST_MONITORING_DELAY, host.hostname))


@receiver(pre_save, sender=Host)
@receiver(pre_delete, sender=Host)
def preserve_hostname(sender, **kwargs):
    """
    When saving a host, if its hostname changes, set an old_hostname
    attribute on the object, so that later post_save signals can use it.
    """
    host = kwargs.get('instance')
    try:
        old_host = host.__class__.objects.get(id=host.id)
        host.old_hostname = old_host.hostname
    except Host.DoesNotExist:
        host.old_hostname = host.hostname


@receiver(post_save, sender=Host)
def update_host_dns_record(sender, **kwargs):
    """
    Use the old_hostname attribute set by the preserve_hostname signal
    to find an existing canonical address assignment and update it.
    """
    if 'dewey.networks' in settings.INSTALLED_APPS and settings.TASKS_ENABLED:
        from dewey.networks.tasks import create_dns_records, delete_dns_records
        host = kwargs.get('instance')
        canonical = host.canonical_assignment
        if canonical:
            if host.hostname != host.old_hostname:
                logger.debug('updating dns records for {} (formerly {})'.format(host.hostname, host.old_hostname))
                # First construct a transient Host object with the old hostname; we never save this,
                # just use it in our transient AddressAssignment object ...
                old_host = copy.deepcopy(host)
                old_host.hostname = host.old_hostname
                # Then construct a transient AddressAssignment (again never saved),
                # because our tasks for managing records operate on AddressAssignment objects
                old_assignment = copy.deepcopy(canonical)
                old_assignment.host = old_host
                # Chain together two tasks, using their immutable signatures; this forces the two
                # tasks to run consecutively, without passing their output to each other.
                tasks = chain(delete_dns_records.si(old_assignment), create_dns_records.si(canonical))
                return tasks()
