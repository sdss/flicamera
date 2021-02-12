#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-20
# @Filename: mock.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import ctypes
import errno
import time
import unittest.mock

import numpy

import flicamera.lib

from .camera import FLICameraSystem


DEV_COUNTER = 0


async def get_mock_camera_system(devices: dict, camera_config={}) -> FLICameraSystem:
    """Returns a camera system with mock devices attached."""

    with unittest.mock.patch("ctypes.cdll.LoadLibrary", MockLibFLI):

        camera_system = FLICameraSystem(
            simulation_mode=True,
            camera_config=camera_config,
        )

        assert isinstance(camera_system.lib.libc, MockLibFLI)
        camera_system.lib.libc.devices = []

        for devname in devices:
            device = MockFLIDevice(devname, **devices[devname]["params"])
            camera_system.lib.libc.devices.append(device)

        camera_system.setup()
        for camera in devices:
            await camera_system.add_camera(uid=camera)

        return camera_system


class MockFLIDevice(object):
    """A mock FLI device."""

    _defaults = {
        "temperature": {"CCD": 0, "base": 0},
        "cooler_power": 0,
        "serial": "ML0000",
        "exposure_time_left": 0,
        "exposure_time": 0,
        "exposure_status": "idle",
        "model": "MicroLine ML50100",
        "exposure_start_time": 0,
        "ul_x": 0,
        "ul_y": 0,
        "lr_x": 512,
        "lr_y": 512,
    }

    def __init__(self, name, **kwargs):

        global DEV_COUNTER

        self.dev = DEV_COUNTER
        DEV_COUNTER += 1

        self.name = name

        self.reset_defaults()
        self.state.update(kwargs)

        self.image = None
        self.row = 0

    def reset_defaults(self):
        """Resets the device to the default state."""

        self.state = self._defaults.copy()
        self.row = 0


class MockLibFLI(ctypes.CDLL):
    """Mocks the CDLL object with the FLI dynamic library."""

    def __init__(self, dlpath: str):

        self.dlpath: str = dlpath
        self.devices: list[MockFLIDevice] = []

        self.restype = flicamera.lib.chk_err

    def reset(self):
        """Resets the initial values of the mocked device."""

        self.__init__(self.dlpath)

    def __getattr__(self, name):

        # __getattr__ only gets called if there is no attribute in the class
        # that matches that name. So for the cases when we haven't overridden
        # the library function, we returns a Mock that returns 0 (no error).

        if name.startswith("FLI"):
            return unittest.mock.MagicMock(retur_value=self.restype(0))

    def _get_device(self, dev):
        """Gets the appropriate device."""

        if isinstance(dev, ctypes.c_long):
            dev = dev.value

        for device in self.devices:
            if device.dev == dev:
                return device

        return None

    def FLIList(self, domain, names_ptr):

        device_names = [
            (dev.name + ";" + dev.state["model"]).encode() for dev in self.devices
        ]

        # names_ptr is a pointer to a pointer to a char pointer (yep).
        # We create a char pointer array with the length of the devices and
        # unpack the above device_names into it.
        # See https://stackoverflow.com/a/4145859 for details.
        # Then we access the object to which the names_ptr points to and
        # replace its contents.
        names_ptr._obj.contents = (ctypes.c_char_p * len(self.devices))(*device_names)

        return self.restype(0)

    def FLIOpen(self, dev_ptr, name, domain):

        name = name.decode()
        for device in self.devices:
            if device.name == name:
                dev_ptr._obj.value = device.dev
                return 0

        return self.restype(-errno.ENXIO)

    def FLIClose(self, dev):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        return self.restype(0)

    def FLIGetSerialString(self, dev, serial_ptr, str_size):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        serial_ptr.value = device.state["serial"].encode()

        return self.restype(0)

    def FLIGetModel(self, dev, model_ptr, str_size):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        model_ptr.value = device.state["model"].encode()

        return self.restype(0)

    def FLISetExposureTime(self, dev, exp_time):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        if isinstance(exp_time, ctypes._SimpleCData):
            device.state["exposure_time"] = exp_time.value
        else:
            device.state["exposure_time"] = exp_time

        return self.restype(0)

    def FLISetTemperature(self, dev, temperature):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        device.state["temperature"]["CCD"] = temperature.value

        return self.restype(0)

    def FLIReadTemperature(self, dev, temp_flag, temp_ptr):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        if temp_flag == flicamera.lib.FLI_TEMPERATURE_CCD:
            temp_ptr._obj.value = device.state["temperature"]["CCD"]
        elif temp_flag == flicamera.lib.FLI_TEMPERATURE_BASE:
            temp_ptr._obj.value = device.state["temperature"]["base"]

        return self.restype(0)

    def FLIGetCoolerPower(self, dev, cooler_ptr):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        cooler_ptr._obj.value = device.state["cooler_power"]

        return self.restype(0)

    def FLIGetExposureStatus(self, dev, timeleft_ptr):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        if device.state["exposure_status"] == "idle":
            timeleft_ptr._obj.value = 0
        elif device.state["exposure_status"] == "exposing":

            time_elapsed = 1000 * (time.time() - device.state["exposure_start_time"])
            if time_elapsed > device.state["exposure_time"]:
                timeleft_ptr._obj.value = 0
            else:
                time_left = int(device.state["exposure_time"] - time_elapsed)
                timeleft_ptr._obj.value = time_left

        return self.restype(0)

    def FLIExposeFrame(self, dev):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        if device.state["exposure_status"] != "idle":
            return self.restype(-errno.EALREADY)

        device.state["exposure_status"] = "exposing"
        device.state["exposure_start_time"] = time.time()

        device.row = 0  # Reset readout row

        return self.restype(0)

    def FLICancelExposure(self, dev):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        device.state["exposure_status"] = "idle"
        device.state["exposure_time_left"] = 0

        return self.restype(0)

    def FLIGetVisibleArea(self, dev, ul_x_ptr, ul_y_ptr, lr_x_ptr, lr_y_ptr):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        ul_x_ptr._obj.value = device.state["ul_x"]
        ul_y_ptr._obj.value = device.state["ul_y"]
        lr_x_ptr._obj.value = device.state["lr_x"]
        lr_y_ptr._obj.value = device.state["lr_y"]

        return self.restype(0)

    def FLIGrabRow(self, dev, array_ptr, col_size):

        device = self._get_device(dev)
        if not device:
            return self.restype(-errno.ENXIO)

        if not device.state["exposure_status"] == "exposing":
            return self.restype(-errno.ENXIO)

        time_left = ctypes.c_long()
        self.FLIGetExposureStatus(dev, ctypes.byref(time_left))

        if time_left.value > 0:
            return self.restype(-errno.ENXIO)

        if device.row == 0 and device.image is None:

            n_rows = device.state["lr_y"] - device.state["ul_y"]
            n_cols = device.state["lr_x"] - device.state["ul_x"]

            image = numpy.zeros((n_rows, n_cols), dtype=numpy.uint16) + 500
            device.image = numpy.random.poisson(image)

        # This is a hack ... but there doesn't seem to be another way to access
        # the memory address. In principle byref(img_ptr.contents, offset)
        # should send a pointer pointing to the address of the first element
        # in the array plus the offset, but this function always seems to get
        # the initial address of the array regardless of the offset. This may
        # be due to the fact that this function is Python and not C ... In any
        # case, we can get the value of each memory address that would
        # correspond to this row and assign it. It's very slow  because it
        # iterates over each elements, so do not use with large image.
        initial_address = ctypes.addressof(array_ptr._obj)
        for ii in range(col_size):

            offset = device.row * col_size + ii
            address = initial_address + offset * ctypes.sizeof(ctypes.c_uint16)

            (ctypes.c_uint16).from_address(address).value = device.image[device.row, ii]

        device.row += 1

        return self.restype(0)
