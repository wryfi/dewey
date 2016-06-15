import csv
import re

from django.core.management.base import BaseCommand

from environments.models import Safe, Secret

class Command(BaseCommand):
    help = 'import and export secrets'

    def add_arguments(self, parser):
        parser.add_argument('action', help='import or export')
        parser.add_argument('--file', '-f', help='filename')

    def handle(self, *args, **options):
        self.file = options['file']
        if options['action'] == 'import':
            self.import_secrets()
        elif options['action'] == 'export':
            self.export_secrets()

    def export_secrets(self):
        rows = [['name', 'safe', 'secret']]
        for secret in Secret.objects.all():
            rows.append([secret.name, secret.safe.id, secret.export_format])
        with open(self.file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

    def import_secrets(self):
        with open(self.file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                safe = Safe.objects.get(id=row['safe'])
                if re.match(r'.*::.*::vault:v\d:.*', row['secret']):
                    imported_secret = row['secret'].split('::')[-1]
                else:
                    imported_secret = row['secret']
                try:
                    secret = Secret.objects.get(name=row['name'], safe=safe)
                    secret.secret = imported_secret
                except Secret.DoesNotExist:
                    secret = Secret(name=row['name'], safe=safe, secret=imported_secret)
                secret.save()
