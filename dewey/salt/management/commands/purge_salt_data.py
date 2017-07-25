import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from dewey.salt.models import Highstate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'remove stale salt data per settings.SALT_HIGHSTATE_*_DAYS'

    def _get_retention_seconds(self, changes=None, errors=None):
        if changes and errors:
            return max(settings.SALT_HIGHSTATE_CHANGE_DAYS * 86400, settings.SALT_HIGHSTATE_ERROR_DAYS * 86400)
        elif changes and not errors:
            return settings.SALT_HIGHSTATE_CHANGE_DAYS * 86400
        elif errors and not changes:
            return settings.SALT_HIGHSTATE_ERROR_DAYS * 86400
        else:
            return settings.SALT_HIGHSTATE_DAYS * 86400

    def handle(self, *args, **options):
        now = timezone.now()
        for highstate in Highstate.objects.all():
            delta = now - highstate.received
            retention_seconds = self._get_retention_seconds(highstate.statechange_set.all(),
                                                            highstate.stateerror_set.all())
            if delta.total_seconds() > retention_seconds:
                highstate.delete()
                logger.info(
                    'deleted highstate {} that was over {} seconds old'.format(highstate.jid, retention_seconds))
            else:
                logger.debug(
                    'kept highstate {} that was less than {} seconds old'.format(highstate.jid, retention_seconds))
