#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-05-08
# @Filename: configuration.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import os

import ruamel.yaml


def merge_config(user, default):
    """Merges a user configuration with the default one."""

    if isinstance(user, dict) and isinstance(default, dict):
        for kk, vv in default.items():
            if kk not in user:
                user[kk] = vv
            else:
                user[kk] = merge_config(user[kk], vv)

    return user


def get_config(name, allow_user=True, user_path=None, config_envvar=None,
               merge_mode='update'):
    """Returns a configuration dictionary.

    The configuration dictionary is created by merging the default
    configuration file that is part of the library (in ``etc/<name>.yml``)
    with a user configuration file. The path to the user configuration file
    can be defined as an environment variable to be passed to this function
    in ``config_envvar`` or as a path in ``user_path``. The environment
    variable, if exists, always takes precedence.

    Parameters
    ----------
    name : str
        The name of the package.
    allow_user : bool
        If `True`, looks for an user configuration file and merges is to the
        default configuration. Otherwise it returns just the default
        configuration.
    user_path : str
        The path to the user configuration file. Defaults to
        ``~/.config/<name>/<name>.yml``. Ignored if the file does not exist.
    config_envvar : str
        The environment variable that contains the path to the user
        configuration file. Defaults to ``<name>_CONFIG_PATH``. If the
        environment variable exists, the ``user_path`` is ignored.
    merge_mode : str
        Defines how the default and user dictionaries will be merged. If
        ``update``, the user dictionary will be used to update the default
        configuration. If ``replace``, only the user configuration will be
        returned.

    Returns
    -------
    config : dict
        A dictionary containing the configuration.

    """

    assert merge_mode in ['update', 'replace'], 'invalid merge mode.'

    # Loads config
    yaml = ruamel.yaml.YAML(typ='safe')
    config = yaml.load(open(os.path.join(os.path.dirname(__file__),
                                         '../etc/{0}.yml'.format(name))))

    if allow_user is False:
        return config

    config_envvar = config_envvar or '{}_CONFIG_PATH'.format(name.upper())

    if user_path is not None:
        user_path = os.path.expanduser(os.path.expandvars(user_path))
    else:
        user_path = os.path.expanduser('~/.config/{0}/{0}.yml'.format(name))

    if config_envvar in os.environ:
        custom_config_fn = os.environ[config_envvar]
    elif os.path.exists(user_path):
        custom_config_fn = user_path
    else:
        return config

    user_config = yaml.load(open(custom_config_fn)) or {}

    if merge_mode == 'update':
        return merge_config(user_config, config)
    else:
        return user_config
