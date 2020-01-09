#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-07
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from basecam import BaseCamera, CameraSystem

import flicamera.lib


class FLICameraSystem(CameraSystem):

    def __init__(self, *args, **kwargs):

        self.lib = flicamera.lib.LibFLI()

    def list_available_cameras(self):

        return self.lib.list_cameras()


class FLICamera(BaseCamera):

    async def _connect_internal(self, **config_params):
        """Internal method to connect the camera."""

        pass

    async def _status_internal(self):
        """Gets a dictionary with the status of the camera.

        Returns
        -------
        status : dict
            A dictionary with status values from the camera (e.g.,
            temperature, cooling status, firmware information, etc.)

        """

        pass

    async def _expose_internal(self, exposure_time):
        """Internal method to handle camera exposures.

        Returns
        -------
        fits : `~astropy.io.fits.HDUList`
            An HDU list with a single extension containing the image data
            and header.

        """

        pass

    @property
    def _uid_internal(self):
        """Get the unique identifier from the camera (e.g., serial number).

        Returns
        -------
        uid : str
            The unique identifier for this camera.

        """

        return None

    async def _disconnect_internal(self):
        """Internal method to disconnect a camera."""

        pass
