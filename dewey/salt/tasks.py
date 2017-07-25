import logging

from django.core.management import call_command
from celery import shared_task

logger = logging.getLogger('.'.join(['dewey', __name__]))


@shared_task(default_retry_delay=300, max_retries=1)
def clean_up_highstates():
    logger.info('Cleaning up highstates')
    try:
        call_command('purge_salt_data')
    except Exception as ex:
        logger.error('There was an error calling purge_salt_data: {}'.format(ex))
        raise clean_up_highstates.retry(exc=ex)