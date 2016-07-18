from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


WARNING = '''
WARNING: Running this script will permanently delete the content types
associated with the selected application. This is a destructive action
that should only be taken if you know what you are doing, and have a
recent database backup at hand.

Before continuing, you should also remove any references, especially in
Generic Foreign Keys, to the content types you are deleting.

'''


class Command(BaseCommand):
    help = 'removes contenttypes from app'

    def add_arguments(self, parser):
        parser.add_argument('--app', '-a', help='application to clean up', required=True)

    def handle(self, *args, **options):
        self.stdout.write(WARNING)
        response = input('Are you sure you want to continue? [y|n] ')
        ctypes = ContentType.objects.all().order_by('app_label', 'model')
        if response.lower() == 'y':
            self.stdout.write('cleaning up contenttypes for {}'.format(options['app']))
            for ctype in ctypes:
                if ctype.app_label == options['app']:
                    self.stdout.write('deleting contenttype {}:{}'.format(ctype.app_label, ctype.model))
                    ctype.delete()
