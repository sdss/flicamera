#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-09
# @Filename: flicamera_tests.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

# These are not unit tests and are meant to be run with a real camera connected.

import asyncio

import flicamera


async def main():

    camera_system = flicamera.FLICameraSystem()
    serials = camera_system.list_available_cameras()

    camera = await camera_system.add_camera(uid=serials[0])

    await camera.connect()

    exposure = await camera.flat(1.)
    exposure.write('test.fits')


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    loop.run_forever()
