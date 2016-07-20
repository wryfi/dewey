import logging
from datetime import timedelta

from django.db.models.signals import post_save
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
