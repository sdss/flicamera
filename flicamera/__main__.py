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
import warnings
from functools import wraps

import click

from basecam.exposure import ImageNamer
from clu.actor import TimerCommand
from sdsstools import read_yaml_file

from flicamera import __version__, log
from flicamera.actor import FLIActor
from flicamera.camera import FLICamera, FLICameraSystem


def cli_coro(f):
    """Decorator function that allows defining coroutines with click."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


class FLICameraSystemWrapper(object):
    """A helper to store CameraSystem initialisation parameters."""

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs

        self.camera_system = None

    async def __aenter__(self):

        config_path = self.kwargs.pop('config_path', None)

        self.camera_system = FLICameraSystem(*self.args, **self.kwargs)

        if not self.kwargs.get('verbose', False):
            self.camera_system.logger.handlers[0].setLevel(logging.ERROR)

        if config_path:
            self.camera_system.logger.debug(f'loaded configuration file {config_path}')

        self.camera_system.setup()
        await self.camera_system.start_camera_poller()
        await asyncio.sleep(0.1)  # Some time to allow camera to connect.

        return self.camera_system

    async def __aexit__(self, *excinfo):

        for camera in self.camera_system.cameras:
            await camera.disconnect()

        await self.camera_system.disconnect()


pass_camera_system = click.make_pass_decorator(FLICameraSystemWrapper,
                                               ensure=True)


@click.group(invoke_without_command=True)
@click.option('--cameras', type=str, required=False, show_envvar=True,
              help='Comma-separated list of camera names to connect.')
@click.option('-c', '--config', 'config_path', show_envvar=True,
              type=click.Path(exists=True, dir_okay=False),
              help='Path to configuration file. Defaults to $SDSSCORE_DIR.')
@click.option('-p', '--port', type=int, show_default=True, show_envvar=True,
              default=19995, help='Port on which to run the actor.')
@click.option('-n', '--actor-name', type=str, show_default=True,
              show_envvar=True, default='flicamera',
              help='The name of the actor.')
@click.option('--no-log', is_flag=True, allow_from_autoenv=False,
              help='Disable logging.')
@click.option('-v', '--verbose', is_flag=True, allow_from_autoenv=False,
              help='Output to stdout.')
@click.pass_context
@cli_coro
async def flicamera(ctx, cameras, config_path, port, actor_name, no_log, verbose):
    """Command Line Interface for Finger Lakes Instrumentation cameras.

    When called by itself this command will start a TCP actor accessible
    on 127.0.0.1:port.

    """

    if verbose:
        log.set_level(logging.NOTSET)
    else:
        log.set_level(logging.ERROR)

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
        if no_log:
            log_file = None
        else:
            log_file = config.get('log_file', None)
            if log_file:
                log_file = log_file.format(hostname=socket.getfqdn())
    else:
        log_file = None
        camera_config = None

    include = cameras or None

    ctx.obj = FLICameraSystemWrapper(camera_config=camera_config,
                                     include=include,
                                     log_file=log_file,
                                     verbose=verbose,
                                     config_path=config_path)

    if ctx.invoked_subcommand is None:

        async with ctx.obj as fli:

            actor_params = {'name': actor_name,
                            'host': 'localhost',
                            'port': port,
                            'version': __version__,
                            'verbose': verbose}
            if config and 'actor' in config:
                actor_params.update(config['actor'])

            if 'log_dir' in actor_params and no_log is False:
                log_dir = actor_params['log_dir'].format(actor_name=actor_name)
                actor_params['log_dir'] = log_dir

            # By default the image namer writes to ./ For production we want to
            # write to /data but we'll define that in the config file.
            data_dir = actor_params.pop('data_dir', './')
            FLICamera.image_name = ImageNamer('{camera.uid}-{num:04d}.fits',
                                              dirname=data_dir, overwrite=False)

            if cameras:
                actor_params.update({'default_cameras': list(cameras)})

            actor = await FLIActor(fli, **actor_params).start()
            actor.timer_commands.append(TimerCommand('status', delay=60))

            await actor.run_forever()


@flicamera.command()
@pass_camera_system
@cli_coro
async def status(camera_system):
    """Returns the status of the connected cameras."""

    async with camera_system as fli:

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
@pass_camera_system
@cli_coro
async def expose(camera_system, exptime, outfile, overwrite):
    """Returns the status of the connected cameras."""

    async with camera_system as fli:

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
