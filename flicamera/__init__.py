# encoding: utf-8

# flake8: noqa
# isort:skip_file

import os
import warnings

from .utils import get_config, get_logger


__version__ = '0.1.0-alpha.0'

NAME = 'flicamera'


config = get_config(NAME, allow_user=True)

log = get_logger('flicamera')
