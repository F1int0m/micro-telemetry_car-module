# flake8: noqa
from .base import *

try:
    from .local import *
except ImportError:
    print('Not found local.py')
