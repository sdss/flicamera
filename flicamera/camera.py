#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-07
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import time
import warnings

from typing import Any, Dict, List, Optional, Tuple, Type

import astropy.time

from basecam import BaseCamera, CameraEvent, CameraSystem, Exposure
from basecam.exceptions import CameraConnectionError, ExposureError
from basecam.mixins import CoolerMixIn, ExposureTypeMixIn, ImageAreaMixIn

import flicamera
from flicamera.lib import FLIError, FLIWarning, LibFLI, LibFLIDevice
from flicamera.model import flicamera_model


__all__ = ["FLICameraSystem", "FLICamera"]


class FLICamera(BaseCamera, ExposureTypeMixIn, CoolerMixIn, ImageAreaMixIn):
    """A FLI camera."""

    camera_system: FLICameraSystem
    _device: LibFLIDevice

    fits_model = flicamera_model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gain: float = self.camera_params.get("gain", -999)
        self.read_noise: float = self.camera_params.get("read_noise", -999)

        self.observatory: str = flicamera.OBSERVATORY
        if self.observatory in flicamera.config["pixel_scale"]:
            self.pixel_scale: float = flicamera.config["pixel_scale"][self.observatory]
        else:
            self.pixel_scale: float = -999.0

    async def _connect_internal(self, **conn_params):
        """Internal method to connect the camera."""

        serial = conn_params.get("serial", conn_params.get("uid", self.uid))

        if serial is None:
            raise CameraConnectionError("unknown serial number.")

        _device = self.camera_system.lib.get_camera(serial)

        if _device is None:
            raise CameraConnectionError(f"cannot find camera with serial {serial}.")

        self._device = _device

        temp_setpoint = self.camera_params.get("temperature_setpoint", False)
        if temp_setpoint:
            asyncio.create_task(self.set_temperature(temp_setpoint))

    def _status_internal(self) -> Dict[str, Any] | None:
        """Gets a dictionary with the status of the camera.

        Returns
        -------
        status
            A dictionary with status values from the camera (e.g.,
            temperature, cooling status, firmware information, etc.)
        """

        device = self._device

        try:
            device._update_temperature()
        except FLIError as err:
            if "No such device" in str(err):
                warnings.warn("Camera disconnected", FLIWarning)
                asyncio.create_task(self.camera_system.remove_camera(uid=self.uid))
                return None
            raise
        except Exception:
            raise

        return dict(
            model=device.model,
            serial=device.serial,
            fwrev=device.fwrev,
            hwrev=device.hwrev,
            hbin=device.hbin,
            vbin=device.vbin,
            visible_area=device.get_visible_area(),
            image_area=device.area,
            temperature_ccd=device._temperature["CCD"],
            temperature_base=device._temperature["base"],
            exposure_time_left=device.get_exposure_time_left(),
            cooler_power=device.get_cooler_power(),
        )

    async def _expose_internal(self, exposure: Exposure, **kwargs) -> Exposure:
        """Internal method to handle camera exposures."""

        if not exposure.exptime:
            raise ExposureError("Exposure time not set.")

        TIMEOUT = 5

        device = self._device

        device.cancel_exposure()

        device.set_exposure_time(exposure.exptime)

        image_type = exposure.image_type
        frametype = "dark" if image_type in ["dark", "bias"] else "normal"

        device.start_exposure(frametype)

        exposure.obstime = astropy.time.Time.now()

        start_time = time.time()

        time_left = exposure.exptime

        while True:

            await asyncio.sleep(time_left)

            time_left = device.get_exposure_time_left() / 1000.0

            if time_left == 0:
                self.notify(CameraEvent.EXPOSURE_READING)
                array = await self.loop.run_in_executor(None, device.read_frame)
                exposure.data = array
                return exposure

            if time.time() - start_time > exposure.exptime + TIMEOUT:
                raise ExposureError("timeout while waiting for exposure to finish.")

    async def _get_temperature_internal(self) -> float:
        """Internal method to get the camera temperature."""

        self._device._update_temperature()
        return self._device._temperature["CCD"]

    async def _set_temperature_internal(self, temperature: float):
        """Internal method to set the camera temperature."""

        self._device.set_temperature(temperature)

    async def _get_image_area_internal(self) -> Tuple[int, int, int, int]:
        """Internal method to return the image area."""

        area = self._device.area

        # Convert from (ul_x, ul_y, lr_x, lr_y) to (x0, x1, y0, y1)
        area = (area[0], area[2], area[1], area[3])

        return area

    async def _set_image_area_internal(
        self,
        area: Optional[Tuple[int, int, int, int]] = None,
    ):
        """Internal method to set the image area."""

        if area:
            # Convert from (x0, x1, y0, y1) to (ul_x, ul_y, lr_x, lr_y)
            area = (area[0], area[2], area[1], area[3])

        self._device.set_image_area(area)

    async def _get_binning_internal(self) -> Tuple[int, int]:
        """Internal method to return the binning."""

        return (self._device.hbin, self._device.vbin)

    async def _set_binning_internal(self, hbin, vbin):
        """Internal method to set the binning."""

        self._device.set_binning(hbin, vbin)


class FLICameraSystem(CameraSystem[FLICamera]):
    """FLI camera system."""

    __version__ = flicamera.__version__  # type: ignore

    camera_class = FLICamera

    def __init__(self, *args, simulation_mode=False, **kwargs):

        self.camera_class: Type[FLICamera] = kwargs.pop("camera_system", FLICamera)
        self.lib = LibFLI(simulation_mode=simulation_mode)

        super().__init__(*args, **kwargs)

    def list_available_cameras(self) -> List[str]:

        # These are camera devices, not UIDs. They can change as cameras
        # are replugged or moved to a different computer.
        devices_id = self.lib.list_cameras()

        # Get the serial number as UID.
        serial_numbers = []
        for device_id in devices_id:
            try:
                device = LibFLIDevice(device_id, self.lib.libc)
                serial_numbers.append(device.serial)
            except FLIError:
                continue

        return serial_numbers
