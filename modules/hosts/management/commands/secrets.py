from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'imports and exports secrets'

    def add_arguments(self, parser):
        parser.add_argument('action', help='import or export')
        parser.add_argument('--import-dir', '-d', help='directory from which to import')
        parser.add_argument('--out-file', '-o', help='output file')

    def handle(self, *args, **options):
        print(options)