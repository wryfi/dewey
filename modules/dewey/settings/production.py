from .common import *
import os

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

DEBUG = False

