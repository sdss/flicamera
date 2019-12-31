# encoding: utf-8

# flake8: noqa
# isort:skip_file

from sdsstools import get_config, get_logger, get_package_version


NAME = 'flicamera'

__version__ = get_package_version(__file__, 'sdss-flicamera') or 'dev'

config = get_config(NAME, allow_user=True)
log = get_logger(NAME)
