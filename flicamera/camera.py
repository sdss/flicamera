#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-07
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import time

import astropy

from basecam import BaseCamera, CameraEvent, CameraSystem, exceptions
from basecam.mixins import CoolerMixIn, ExposureTypeMixIn, ImageAreaMixIn
from basecam.models import basic_fz_fits_model

import flicamera
import flicamera.lib


__all__ = ['FLICameraSystem', 'FLICamera']


class FLICamera(BaseCamera, ExposureTypeMixIn, CoolerMixIn, ImageAreaMixIn):

    _device = None
    fits_model = basic_fz_fits_model

    async def _connect_internal(self, **conn_params):
        """Internal method to connect the camera."""

        serial = conn_params.get('serial', conn_params.get('uid', self.uid))

        if serial is None:
            raise exceptions.CameraConnectionError('unknown serial number.')

        self._device = self.camera_system.lib.get_camera(serial)

        if self._device is None:
            raise exceptions.CameraConnectionError(f'cannot find camera '
                                                   f'with serial {serial}.')

    def _status_internal(self):
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
                    hbin=device.hbin,
                    vbin=device.vbin,
                    visible_area=device.get_visible_area(),
                    image_area=device.area,
                    temperature_ccd=device._temperature['CCD'],
                    temperature_base=device._temperature['base'],
                    exposure_time_left=device.get_exposure_time_left(),
                    cooler_power=device.get_cooler_power())

    async def _expose_internal(self, exposure, **kwargs):
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

        device.set_exposure_time(exposure.exptime)

        image_type = exposure.image_type
        frametype = 'dark' if image_type in ['dark', 'bias'] else 'normal'

        device.start_exposure(frametype)

        exposure.obstime = astropy.time.Time.now()
        self._notify(CameraEvent.EXPOSURE_INTEGRATING)

        start_time = time.time()
        time_left = exposure.exptime

        while True:

            await asyncio.sleep(time_left)

            time_left = device.get_exposure_time_left() / 1000.

            if time_left == 0:
                self._notify(CameraEvent.EXPOSURE_READING)
                array = await self.loop.run_in_executor(None, device.read_frame)
                exposure.data = array
                return exposure

            if time.time() - start_time > exposure.exptime + TIMEOUT:
                raise exceptions.ExposureError('timeout while waiting for '
                                               'exposure to finish.')

    async def _get_temperature_internal(self):
        """Internal method to get the camera temperature."""

        self._device._update_temperature()
        return self._device._temperature['CCD']

    async def _set_temperature_internal(self, temperature):
        """Internal method to set the camera temperature."""

        self._device.set_temperature(temperature)

    async def _get_image_area_internal(self):
        """Internal method to return the image area."""

        area = self._device.area

        # Convert from (ul_x, ul_y, lr_x, lr_y) to (x0, x1, y0, y1)
        area = (area[0], area[2], area[1], area[3])

        return area

    async def _set_image_area_internal(self, area=None):
        """Internal method to set the image area."""

        if area:
            # Convert from (x0, x1, y0, y1) to (ul_x, ul_y, lr_x, lr_y)
            area = (area[0], area[2], area[1], area[3])

        self._device.set_image_area(area)

    async def _get_binning_internal(self):
        """Internal method to return the binning."""

        return (self._device.hbin, self._device.vbin)

    async def _set_binning_internal(self, hbin, vbin):
        """Internal method to set the binning."""

        self._device.set_binning(hbin, vbin)


class FLICameraSystem(CameraSystem):
    """Initialises the camera system."""

    __version__ = flicamera.__version__

    camera_class = FLICamera

    def __init__(self, *args, **kwargs):

        self.camera_class = kwargs.pop('camera_system', FLICamera)
        self.lib = flicamera.lib.LibFLI()

        super().__init__(*args, **kwargs)

    def list_available_cameras(self):

        # These are camera devices, not UIDs. They can change as cameras
        # are replugged or moved to a different computer.
        devices_id = self.lib.list_cameras()

        # Get the serial number as UID.
        serial_numbers = []
        for device_id in devices_id:
            device = flicamera.lib.LibFLIDevice(device_id, self.lib.libc)
            serial_numbers.append(device.serial)

        return serial_numbers
