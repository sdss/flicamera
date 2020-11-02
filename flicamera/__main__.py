#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-22
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import logging
import os
import socket

import click
from click_default_group import DefaultGroup

from basecam.exposure import ImageNamer
from clu.command import TimedCommand
from sdsstools import get_logger, read_yaml_file
from sdsstools.daemonizer import DaemonGroup, cli_coro

from flicamera import NAME, __version__
from flicamera.actor import FLIActor
from flicamera.camera import FLICamera, FLICameraSystem


log = get_logger(NAME)

# Set default image namer
FLICamera.image_namer = ImageNamer('{camera.name}-{num:04d}.fits',
                                   overwrite=False)


class FLICameraWrapper(object):
    """A helper to store CameraSystem initialisation parameters."""

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs

        self.camera_system = None

    async def __aenter__(self):

        config_path = self.kwargs.pop('config_path', None)

        self.camera_system = FLICameraSystem(*self.args, **self.kwargs)
        self.camera_system.setup()

        if 'verbose' in self.kwargs and self.kwargs['verbose'] is False:
            self.camera_system.logger.sh.setLevel(logging.WARNING)

        if config_path:
            self.camera_system.logger.debug(f'Loading configuration file '
                                            f'{config_path}')

        await self.camera_system.start_camera_poller()
        await asyncio.sleep(0.1)  # Some time to allow camera to connect.

        return self.camera_system

    async def __aexit__(self, *excinfo):

        for camera in self.camera_system.cameras:
            await camera.disconnect()

        await self.camera_system.disconnect()


@click.group(cls=DefaultGroup, default='actor', default_if_no_args=True)
@click.option('--cameras', type=str, required=False, show_envvar=True,
              help='Comma-separated list of camera names to connect.')
@click.option('-c', '--config', 'config_path', show_envvar=True,
              type=click.Path(exists=True, dir_okay=False),
              help='Path to configuration file. Defaults to $SDSSCORE_DIR.')
@click.option('-v', '--verbose', is_flag=True, allow_from_autoenv=False,
              help='Output extra information to stdout.')
@click.pass_context
def flicamera(ctx, cameras, config_path, verbose):
    """Command Line Interface for Finger Lakes Instrumentation cameras."""

    if verbose:
        log.set_level(logging.NOTSET)
    else:
        log.set_level(logging.WARNING)

    # We want to allow the actor to minimally work without a configuration
    # file so instead of passing it to the actor using the .from_config
    # classmethod we parse the configuration ourselves.

    config = None

    if not config_path:
        config_path = f'{os.path.dirname(__file__)}/etc/flicamera.yaml'
    config = read_yaml_file(config_path)

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

    ctx.obj['camera_system'] = FLICameraWrapper(camera_config=camera_config,
                                                include=include,
                                                log_file=log_file,
                                                verbose=verbose,
                                                config_path=config_path)

    # Store some of the options here for the daemon
    ctx.obj['cameras'] = cameras
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose


@flicamera.group(cls=DaemonGroup, prog='actor', workdir=os.getcwd())
@click.option('-n', '--actor-name', type=str, show_envvar=True,
              help='The name of the actor. Defaults to flicamera.')
@click.option('-h', '--host', type=str, show_envvar=True,
              help='The host on which the actor will run. '
                   'Defaults to localhost.')
@click.option('-p', '--port', type=int, show_envvar=True,
              help='Port on which to run the actor. Defaults to 19995.')
@click.pass_obj
@cli_coro()
async def actor(obj, host, port, actor_name):
    """Start/stop the actor as a daemon."""

    async with obj['camera_system'] as fli:

        if obj['config'] and 'actor' in obj['config']:
            actor_params = obj['config']['actor']
        else:
            actor_params = {}

        actor_params['version'] = __version__
        actor_params['verbose'] = obj['verbose']

        if actor_name:
            actor_params['name'] = actor_name
        if host:
            actor_params['host'] = host
        if port:
            actor_params['port'] = port

        if 'log_dir' in actor_params:
            log_dir = actor_params['log_dir'].format(actor_name=actor_name)
            actor_params['log_dir'] = log_dir

        # By default the image namer writes to ./ For production we want to
        # write to /data but we'll define that in the config file.
        data_dir = actor_params.pop('data_dir', './')

        FLICamera.image_namer.dirname = data_dir

        # We need to change the image namer of any already connected camera.
        for camera in fli.cameras:
            camera.image_namer.dirname = data_dir
            camera.image_namer.camera = camera

        if obj['cameras']:
            actor_params.update({'default_cameras': list(obj['cameras'])})

        actor = await FLIActor(fli, **actor_params).start()
        actor.timed_commands.append(TimedCommand('status', delay=60))

        await actor.run_forever()


@flicamera.command()
@click.pass_obj
@cli_coro()
async def status(obj):
    """Returns the status of the connected cameras."""

    async with obj['camera_system'] as fli:

        if len(fli.cameras) == 0:
            log.error('No cameras connected.')
            return click.Abort()

        for camera in fli.cameras:
            status = camera.get_status()
            key_len = max([len(key) for key in status]) + 1
            print('\nCamera'.ljust(key_len), ': ', camera.name)
            for key, value in status.items():
                if key == 'name':
                    continue
                print(f'{key}'.ljust(key_len), ': ', value)


@flicamera.command()
@click.argument('EXPTIME', default=1, type=float, required=False)
@click.argument('OUTFILE', type=click.Path(dir_okay=False), required=False)
@click.option('--overwrite', is_flag=True, help='Overwrite existing images.')
@click.pass_obj
@cli_coro()
async def expose(obj, exptime, outfile, overwrite):
    """Returns the status of the connected cameras."""

    async with obj['camera_system'] as fli:

        log.debug('starting camera exposures ... ')
        exposures = await asyncio.gather(*[camera.expose(exptime)
                                           for camera in fli.cameras],
                                         return_exceptions=False)

        log.debug('writing images to disk ... ')
        writers = []
        for exposure in exposures:
            if outfile:
                outfile = outfile.format(camera=exposure.camera)
                writers.append(exposure.write(filename=outfile,
                                              overwrite=overwrite))
            else:
                writers.append(exposure.write(overwrite=overwrite))

        await asyncio.gather(*writers, return_exceptions=True)


def main():
    flicamera(obj={}, auto_envvar_prefix='FLICAMERA')


if __name__ == '__main__':
    main()
