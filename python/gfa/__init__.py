# encoding: utf-8

# flake8: noqa
# isort:skip_file

import os
import warnings

from .utils import get_config, get_logger

import pkg_resources


try:
    __version__ = pkg_resources.get_distribution('gfa').version
except pkg_resources.DistributionNotFound:
    try:
        import toml
        poetry_config = toml.load(open(os.path.join(os.path.dirname(__file__),
                                                    '../../pyproject.toml')))
        __version__ = poetry_config['tool']['poetry']['version']
    except Exception:
        warnings.warn('cannot find gfa version. Using 0.0.0.', UserWarning)
        __version__ = '0.0.0'


NAME = 'gfa'


config = get_config(NAME, allow_user=True)

log = get_logger('gfa')
