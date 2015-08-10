from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dewey',
        'USER' : 'chaumes',
        'PASSWORD' : get_env('POSTGRES_PASSWORD'),
        'HOST' : 'localhost',
        'PORT' : ''
    },
}
