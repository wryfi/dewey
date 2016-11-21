import os

from .common import *

MEDIA_ROOT = os.path.join(os.environ.get('HOME', '/tmp'), 'share', 'dewey', 'media')
STATIC_ROOT = os.path.join(os.environ.get('HOME', '/tmp'), 'share', 'dewey', 'static')
COMPRESS_ROOT = STATIC_ROOT

DEBUG = True


for backend in TEMPLATES:
    backend['OPTIONS']['debug'] = True

INSTALLED_APPS += (
    'django_extensions', 'debug_toolbar'
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ['127.0.0.1']

ALLOWED_HOSTS = []
NAGIOS_NETWORKS = ['soma']

TASKS_ENABLED = False
