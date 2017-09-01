from .common import *
import os

DEBUG = False

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

SITE_PROTOCOL = 'https'
SITE_DOMAIN = 'dewey.soma.plos.org'

# send logs to syslog
LOGGING['handlers']['syslog'] = {
    'class': 'logging.handlers.SysLogHandler',
    'facility': 3
}
LOGGING['formatters']['syslog'] = {
    'format': '%(asctime)s dewey: [%(name)s:%(lineno)s] %(message)s',
    'datefmt': '%b %d %H:%M:%S'
}
LOGGING['loggers']['django']['handlers'] = ['syslog']
LOGGING['loggers']['dewey']['handlers'] = ['syslog']
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['dewey']['level'] = 'INFO'

