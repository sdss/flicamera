#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-22
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import os
from functools import wraps

import click

from clu.actor import TimerCommand
from sdsstools import read_yaml_file

from flicamera.actor import FLIActor
from flicamera.camera import FLICameraSystem


def cli_coro(f):
    """Decorator function that allows defining coroutines with click."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument('CAMERA-NAME', type=str)
@cli_coro
async def flicamera(camera_name):
    """Starts an actor and sets CAMERA-NAME as the default camera.

    It is expected that the information for the actor is found in
    $SDSSCORE_DIR/configuration_files/actors/flicamera.yaml under the
    actor section. Any additional flags passed are used to override the
    default configuration values.

    """

    config_file = os.path.join(os.environ['SDSSCORE_DIR'],
                               'configuration/actors/flicamera.yaml')

    if not os.path.exists(config_file):
        raise RuntimeError(f'cannot find configuration file {config_file}.')

    actor_config = read_yaml_file(config_file).get('actor', None)
    if not actor_config:
        raise RuntimeError('cannot find actor section in configuration file.')

    if 'log_dir' in actor_config:
        actor_config['log_dir'] = os.path.join(actor_config['log_dir'], camera_name)
    else:
        actor_config['log_dir'] = f'/data/logs/actors/{camera_name}'

    camera_system = FLICameraSystem().setup()
    await camera_system.start_camera_poller()

    await asyncio.sleep(0.1)  # Some time to allow camera to connect.

    actor = await FLIActor.from_config(actor_config, camera_system,
                                       name=camera_name,
                                       default_cameras=[camera_name]).start()
    actor.timer_commands.append(TimerCommand('status', delay=60))

    await actor.run_forever()


if __name__ == '__main__':
    flicamera()
