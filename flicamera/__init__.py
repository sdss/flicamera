# encoding: utf-8

# flake8: noqa
# isort:skip_file

import pathlib

import pkg_resources

from .utils import get_config, get_logger


def get_version():

    try:
        return pkg_resources.get_distribution('sdss-flicamera').version
    except pkg_resources.DistributionNotFound:
        try:
            import toml
            poetry_config = toml.load(
                open(pathlib.Path(__file__).parent / '../../pyproject.toml'))
            return poetry_config['tool']['poetry']['version']
        except Exception:
            return '0.0.0'


NAME = 'flicamera'

__version__ = get_version()

config = get_config(NAME, allow_user=True)

log = get_logger('flicamera')
