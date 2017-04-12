import logging

from celery import shared_task
from django.utils import timezone

from .models import HostMonitoringException


logger = logging.getLogger('.'.join(['dewey', __name__]))


@shared_task(default_retry_delay=60, max_retries=5)
def clean_up_monitoring_exceptions():
    now = timezone.now()
    try:
        for exception in HostMonitoringException.objects.all():
            delta = now - exception.end
            if delta.total_seconds() > 86400:
                exception.delete()
    except Exception as ex:
        raise clean_up_monitoring_exceptions.retry(exc=ex)
