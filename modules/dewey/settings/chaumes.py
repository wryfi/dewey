from .common import *

MEDIA_ROOT = '/home/chaumes/share/dewey/media'
STATIC_ROOT = '/home/chaumes/share/dewey/static'
COMPRESS_ROOT = STATIC_ROOT

DEBUG = True

DATABASES['default']['USER'] = 'chaumes'

for backend in TEMPLATES:
    backend['OPTIONS']['debug'] = True

INSTALLED_APPS += (
    'django_extensions',
)
