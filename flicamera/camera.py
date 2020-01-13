#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-07
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import time

import basecam.exceptions
from basecam import BaseCamera, CameraEvent, CameraSystem, ExposureError

import flicamera.lib


__all__ = ['FLICameraSystem', 'FLICamera']


class FLICameraSystem(CameraSystem):

    def __init__(self, **kwargs):

        self.lib = flicamera.lib.LibFLI()
        super().__init__(FLICamera, **kwargs)

    def list_available_cameras(self):

        # These are camera devices, not UIDs. They can change as cameras
        # are replugged or moved to a different computer.
        devices_id = self.lib.list_cameras()

        # Get the serial number as UID.
        serial_numbers = []
        for device_id in devices_id:
            device = flicamera.lib.FLIDevice(device_id, self.lib.libc)
            serial_numbers.append(device.serial)

        return serial_numbers


class FLICamera(BaseCamera, ExposureTypeMixIn):

    _device = None

    async def _connect_internal(self, serial=None):
        """Internal method to connect the camera."""

        if serial is None:
            serial = self.camera_config.get('uid', None)
            if not serial:
                raise basecam.exceptions.CameraConnectionError('unknown serial number.')

        self._device = self.camera_system.lib.get_camera(serial)

        if self._device is None:
            raise basecam.exceptions.CameraConnectionError(
                f'cannot find camera with serial {serial}.')

    async def _status_internal(self):
        """Gets a dictionary with the status of the camera.

        Returns
        -------
        status : dict
            A dictionary with status values from the camera (e.g.,
            temperature, cooling status, firmware information, etc.)

        """

        device = self._device
        device._update_temperature()

        return dict(model=device.model,
                    serial=device.serial,
                    fwrev=device.fwrev,
                    hwrev=device.hwrev,
                    hbib=device.hbin,
                    vbin=device.vbin,
                    visible_area=device.get_visible_area(),
                    image_area=device.area,
                    temperature_ccd=device._temperature['CCD'],
                    temperature_base=device._temperature['base'],
                    exposure_time_left=device.get_exposure_time_left(),
                    cooler_power=device.get_cooler_power())

    async def _expose_internal(self, exposure_time, image_type='science', **kwargs):
        """Internal method to handle camera exposures.

        Returns
        -------
        fits : `~astropy.io.fits.HDUList` or `~numpy.array`
            An HDU list with a single extension containing the image data
            and header, or a 2D Numpy array.

        """

        TIMEOUT = 5

        device = self._device

        device.cancel_exposure()

        device.set_exposure_time(exposure_time)

        frametype = 'dark' if image_type in ['dark', 'bias'] else 'normal'
        device.start_exposure(frametype)

        self._notify(CameraEvent.EXPOSURE_INTEGRATING)

        start_time = time.time()
        time_left = exposure_time

        while True:

            await asyncio.sleep(time_left)

            time_left = device.get_exposure_time_left() / 1000.

            if time_left == 0:
                self._notify(CameraEvent.EXPOSURE_READING)
                array = device.read_frame()
                return array

            if time.time() - start_time > exposure_time + TIMEOUT:
                raise ExposureError('timeout waiting for exposure to finish.')

    @property
    def _uid_internal(self):
        """Get the unique identifier from the camera (e.g., serial number).

        Returns
        -------
        uid : str
            The unique identifier for this camera.

        """

        return self.get_status()['serial']
