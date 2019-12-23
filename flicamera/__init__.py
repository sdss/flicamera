# encoding: utf-8

# flake8: noqa
# isort:skip_file

import os
import warnings

import pkg_resources

from .utils import get_config, get_logger


try:
    __version__ = pkg_resources.get_distribution('sdss-flicamera').version
except pkg_resources.DistributionNotFound:
    __version__ = 'dev'

NAME = 'flicamera'


config = get_config(NAME, allow_user=True)

log = get_logger('flicamera')
