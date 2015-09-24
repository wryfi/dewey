from requests.auth import HTTPBasicAuth
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from hardware.models import Server

def _get_field(name, fields):
    for field in fields:
        if field['title'] == name:
            return field['values']

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        url = '/'.join([settings.JIRA_URL, 'rest', 'com-spartez-ephor', '1.0', 'search'])
        auth = HTTPBasicAuth(settings.JIRA_USERNAME, settings.JIRA_PASSWORD)
        payload = {'query': 'Category=Servers'}
        request = requests.get(url, auth=auth, params=payload)
        request.raise_for_status()
        assets = [item for item in request.json()['items'] if item['typeName'] == 'Computer']
        for asset in assets:
            status = _get_field('Asset Status', asset['fields'])
            if status[0] == 'Deployed':
              try:
                  server = Server.objects.get(ephor_id=asset['id'])
              except Server.DoesNotExist:
                  server = Server(ephor_id=asset['id'])
              server.asset_tag = _get_field('Title', asset['fields'])[0]
              server.manufacturer = _get_field('Manufacturer', asset['fields'])[0]
              server.model = _get_field('Model', asset['fields'])[0]
              server.serial = _get_field('Serial Number', asset['fields'])[0]
              server.save()
