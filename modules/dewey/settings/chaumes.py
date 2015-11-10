import os

from .common import *

MEDIA_ROOT = os.path.join(os.environ.get('HOME', '/tmp'), 'share', 'dewey', 'media')
STATIC_ROOT = os.path.join(os.environ.get('HOME', '/tmp'), 'share', 'dewey', 'static')
COMPRESS_ROOT = STATIC_ROOT

DEBUG = True

DATABASES['default']['USER'] = 'chaumes'

for backend in TEMPLATES:
    backend['OPTIONS']['debug'] = True

INSTALLED_APPS += (
    'django_extensions',
)

ALLOWED_HOSTS = []
