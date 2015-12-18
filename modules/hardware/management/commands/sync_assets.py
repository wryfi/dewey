from getpass import getpass
from requests.auth import HTTPBasicAuth
import logging
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from hardware.models import Cabinet, CabinetAssignment, Server


logger = logging.getLogger('.'.join(['dewey', __name__]))


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        self.search_url = '/'.join([settings.JIRA_URL, 'rest', 'com-spartez-ephor', '1.0', 'search'])

    def _get_field(self, name, fields):
        ''' Always returns a list, even when there is only one value'''
        for field in fields:
            if field['title'] == name:
                return field['values']

    def _get_auth(self):
        jira_user = settings.JIRA_USERNAME
        jira_password = settings.JIRA_PASSWORD
        if jira_user == '':
            jira_user = input('Jira Username: ')
        if jira_password == '':
            jira_password = getpass('Jira Password: ')
        return HTTPBasicAuth(jira_user, jira_password)

    def _sync_servers(self):
        auth = self._get_auth()
        payload = {'query': 'Type=Computer AND Category=Servers AND plos.assetstatus=Deployed'}
        request = requests.get(self.search_url, auth=auth, params=payload)
        request.raise_for_status()
        assets = [item for item in request.json()['items']]
        for asset in assets:
            status = self._get_field('Asset Status', asset['fields'])
            if len(status) > 0 and status[0] == 'Deployed':
                if self._get_field('Title', asset['fields'])[0] != 'TBD':
                    try:
                        server = Server.objects.get(ephor_id=asset['id'])
                    except Server.DoesNotExist:
                        server = Server(ephor_id=asset['id'])
                    server.asset_tag = self._get_field('Title', asset['fields'])[0]
                    server.manufacturer = self._get_field('Manufacturer', asset['fields'])[0]
                    server.model = self._get_field('Model', asset['fields'])[0]
                    server.serial = self._get_field('Serial Number', asset['fields'])[0]
                    server.save()
                    if not server.cabinets.all():
                        logger.info('server has no cabinet assignments')
                        try:
                            cabinet_name = self._get_field('Location', asset['fields'])[0]
                            logger.info('looking for cabinet named {}'.format(cabinet_name))
                            cabinet = Cabinet.objects.get(slug=cabinet_name)
                            logger.info('adding cabinet assignment: #{} in {}'.format(server.asset_tag, cabinet_name))
                            CabinetAssignment.objects.create(cabinet=cabinet, equipment=server)
                        except Cabinet.DoesNotExist:
                            logger.warning('cabinet {} not found'.format(cabinet_name))
                            pass

    def _sync_storage(self):
        payload = {'query': 'foo'}

    def handle(self, *args, **options):
        self.stdout.write('Synchronizing assets. Please see log file for details.')
        self._sync_servers()

