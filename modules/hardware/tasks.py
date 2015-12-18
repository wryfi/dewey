import logging

from django.core.management import call_command
from django.conf import settings
from celery import shared_task

logger = logging.getLogger('.'.join(['dewey', __name__]))


@shared_task(default_retry_delay=300, max_retries=1)
def sync_assets_task():
    logger.info('Running asset synchronization task')
    if settings.JIRA_USERNAME == '' or settings.JIRA_PASSWORD == '':
        logger.error('Could not sync assets - missing JIRA credentials')
        return
    try:
        call_command('sync_assets')
    except Exception as ex:
        logger.error('There was an error calling sync_assets: {}'.format(ex))
        raise sync_assets_task.retry(exc=ex)