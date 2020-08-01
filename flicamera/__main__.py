#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-22
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import os
import socket
import warnings
from functools import wraps

import click

from basecam.exposure import ImageNamer
from clu.actor import TimerCommand
from sdsstools import read_yaml_file

from flicamera import __version__
from flicamera.actor import FLIActor
from flicamera.camera import FLICamera, FLICameraSystem


def cli_coro(f):
    """Decorator function that allows defining coroutines with click."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument('CAMERAS', type=str, nargs=-1, required=False)
@click.option('-c', '--config', 'config_path', show_envvar=True,
              type=click.Path(exists=True, dir_okay=False),
              help='Camera configuration file. Defaults to $SDSSCORE_DIR.')
@click.option('-p', '--port', type=int, show_default=True, show_envvar=True,
              default=19995, help='Port on which to run the actor.')
@click.option('-n', '--actor-name', type=str, show_default=True,
              show_envvar=True, default='flicamera',
              help='The name of the actor.')
@click.option('-v', '--verbose', is_flag=True,
              help='Output to stdout.')
@cli_coro
async def flicamera(cameras, config_path, port, actor_name, verbose):
    """Starts an actor and sets CAMERAS as the default cameras."""

    # We want to allow the actor to minimally work without a configuration
    # file so instead of passing it to the actor using the .from_config
    # classmethod we parse the configuration ourselves.

    try:
        if not config_path:
            sdsscore = os.environ['SDSSCORE_DIR']
            obs = os.environ['OBSERVATORY'].lower()
            config_path = f'{sdsscore}/configuration/{obs}/actors/flicamera.yaml'
        config = read_yaml_file(config_path)
    except BaseException:
        config = None
        if verbose:
            warnings.warn('Cannot read configuration file. Using defaults.',
                          UserWarning)

    if config:
        if 'cameras' in config:
            camera_config = config['cameras'].copy()
        else:
            camera_config = config.copy()
        log_file = config.get('log_file', None)
        if log_file:
            log_file = log_file.format(hostname=socket.getfqdn())
    else:
        log_file = None
        camera_config = None

    include = cameras or None

    camera_system = FLICameraSystem(camera_config=camera_config,
                                    include=include,
                                    log_file=log_file,
                                    verbose=verbose).setup()
    await camera_system.start_camera_poller()

    await asyncio.sleep(0.1)  # Some time to allow camera to connect.

    actor_params = {'name': actor_name,
                    'host': 'localhost',
                    'port': port,
                    'version': __version__,
                    'verbose': verbose}
    if config and 'actor' in config:
        actor_params.update(config['actor'])

    if 'log_dir' in actor_params:
        actor_params['log_dir'] = actor_params['log_dir'].format(actor_name=actor_name)

    # By default the image namer writes to ./ For production we want to
    # write to /data but we'll define that in the config file.
    data_dir = actor_params.pop('data_dir', './')
    FLICamera.image_name = ImageNamer('{camera.uid}-{num:04d}.fits',
                                      dirname=data_dir, overwrite=False)

    if cameras:
        actor_params.update({'default_cameras': list(cameras)})

    actor = await FLIActor(camera_system, **actor_params).start()
    actor.timer_commands.append(TimerCommand('status', delay=60))

    await actor.run_forever()


def main():
    flicamera(auto_envvar_prefix='FLICAMERA')


if __name__ == '__main__':
    main()
