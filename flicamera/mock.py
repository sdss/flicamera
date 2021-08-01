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
from glob import glob

from typing import Any, Dict, List, Optional, Union

import astropy.io.fits
import astropy.table
import numpy
from photutils.datasets import (
    apply_poisson_noise,
    make_gaussian_sources_image,
    make_noise_image,
)

import flicamera.lib

from .camera import FLICameraSystem


DEV_COUNTER = 0


def read_frame_mock(self):
    """Mock version of `.LibFLIDevice.read_frame` for fast reading."""

    return self.libc._get_image(self.dev)


async def get_mock_camera_system(
    devices: Dict[str, Any],
    camera_config: Dict[str, Any] = {},
    fast_read: bool = True,
) -> FLICameraSystem:
    """Returns a camera system with mock devices attached.

    Parameters
    ----------
    devices
        A dictionary of mocked physical devices. See the documentation for details
        on the format.
    camera_config
        Camera configuration to be passed to `.FLICameraSystem`.
    fast_read
        If `True`, skips reading the mocked image row by row. This is significantly
        faster for large images.
    """

    with unittest.mock.patch("ctypes.cdll.LoadLibrary", MockLibFLI):

        camera_system = FLICameraSystem(
            simulation_mode=True,
            camera_config=camera_config,
        )

        assert isinstance(camera_system.lib.libc, MockLibFLI)
        camera_system.lib.libc.devices = []

        # If read_fast, mock the library read_frame method to immediately return
        # the image array. This helps because FLIGrabRow is very slow if it needs
        # to loop over a large image in Python.
        if fast_read is True:
            flicamera.lib.LibFLIDevice.read_frame = read_frame_mock

        for devname in devices:
            device = MockFLIDevice(
                devname,
                exposure_params=devices[devname].get("exposures", {}),
                status_params=devices[devname].get("params", {}),
            )
            camera_system.lib.libc.devices.append(device)

        camera_system.setup()
        for camera_name in devices:
            await camera_system.add_camera(
                name=camera_name,
                uid=devices[camera_name].get("uid", None),
            )

        return camera_system


def get_source_table(
    param_ranges: dict[str, Any],
    n_sources: int = 1,
) -> astropy.table.Table:
    """Returns a table of sources."""

    def get_random_range(param):
        if isinstance(param_ranges[param], list):
            return numpy.random.uniform(
                param_ranges[param][0],
                param_ranges[param][1],
                n_sources,
            )
        else:
            return [param_ranges[param]] * n_sources

    source_table = astropy.table.Table()
    source_table["amplitude"] = get_random_range("amplitude")
    source_table["x_mean"] = get_random_range("x_mean")
    source_table["y_mean"] = get_random_range("y_mean")
    source_table["theta"] = get_random_range("theta")

    stddev = param_ranges.get("stddev", None)
    if stddev is not None:
        stddev_dev = param_ranges.get("stddev_dev", 0.0)
        if isinstance(stddev, list):
            stddev = numpy.random.uniform(*stddev, n_sources)  # type: ignore
            stddev_source = numpy.random.normal(stddev, stddev_dev)
        else:
            stddev_source = numpy.random.normal(stddev, stddev_dev, n_sources)
        source_table["x_stddev"] = stddev_source
        source_table["y_stddev"] = stddev_source
    else:
        source_table["x_stddev"] = get_random_range("x_stddev")
        source_table["y_stddev"] = get_random_range("y_stddev")

    return source_table


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

    def __init__(
        self,
        name: str,
        status_params: Dict[str, Any] = {},
        exposure_params: Union[str, List[Dict[str, Any]]] = [],
    ):

        global DEV_COUNTER

        self.dev = DEV_COUNTER
        DEV_COUNTER += 1

        self.name = name

        self.state: Dict[str, Any]
        self.reset_defaults()
        self.state.update(status_params)

        self._exposure_params: Union[List[str], List[Dict[str, Any]]]
        self._exposure_idx: int = 0
        self.set_exposure_params(exposure_params)

        self.image: Optional[numpy.ndarray] = None
        self.row = 0

    def reset_defaults(self):
        """Resets the device to the default state."""

        self.state = self._defaults.copy()
        self.row = 0

    def set_exposure_params(self, exposure_params: Union[str, List[Dict[str, Any]]]):
        """Sets the exposure simulation parameters."""

        if isinstance(exposure_params, str):
            self._exposure_params = list(sorted(glob(exposure_params)))
        else:
            self._exposure_params = exposure_params
        self._exposure_idx = 0

    def prepare_image(self):
        """Creates the image that will be fetched."""

        # Default values
        exposure_params: Dict[str, Any] = dict(
            seed=None,
            shape=[
                self.state["lr_x"] - self.state["ul_x"],
                self.state["lr_y"] - self.state["ul_y"],
            ],
            sources=False,
            noise=False,
            apply_poison_noise=False,
        )

        if isinstance(self._exposure_params, list):
            if len(self._exposure_params) == 0:
                # If the simulation configuration doesn't include an "exposures"
                # section, just add some default noise.
                exposure_params["noise"] = {
                    "distribution": "gaussian",
                    "mean": 1000,
                    "stddev": 20.0,
                }
            else:
                this_exposure = self._exposure_params[self._exposure_idx]

                # If str, file is the image to return
                if isinstance(this_exposure, str):
                    data = astropy.io.fits.getdata(this_exposure)
                    return data

                exposure_params.update(this_exposure)

        image = numpy.zeros(exposure_params["shape"][::-1], dtype="float32")
        if "seed" in exposure_params and exposure_params["seed"] is not None:
            numpy.random.seed(exposure_params["seed"])

        if exposure_params["noise"]:
            image += make_noise_image(image.shape, **exposure_params["noise"])

        if exposure_params["sources"]:
            if "source_table" in exposure_params["sources"]:
                source_table = astropy.table.Table.read(
                    exposure_params["sources"]["source_table"]
                )
            else:
                n_sources = exposure_params["sources"]["n_sources"]
                if isinstance(n_sources, list):
                    n_sources = numpy.random.randint(*n_sources)
                param_ranges = exposure_params["sources"]["param_ranges"]
                source_table = get_source_table(param_ranges, n_sources)

            source_image = make_gaussian_sources_image(
                image.shape,
                source_table=source_table,
            )
            source_image *= self.state["exposure_time"] / 1000.0
            image += source_image

            if exposure_params["apply_poison_noise"]:
                image = apply_poisson_noise(image, seed=exposure_params["seed"])

        assert isinstance(image, numpy.ndarray)

        image[image > 2 ** 16] = 2 ** 16 - 1

        self.image = image.astype("uint16")

    def clear_image(self):
        """Clears the image. Called when the buffer has been read."""

        self.image = None
        self.state.update(
            {
                "exposure_time_left": 0,
                "exposure_time": 0,
                "exposure_status": "idle",
                "exposure_start_time": 0,
            }
        )

        if len(self._exposure_params) > 0:
            self._exposure_idx = (self._exposure_idx + 1) % len(self._exposure_params)


class MockLibFLI(ctypes.CDLL):
    """Mocks the CDLL object with the FLI dynamic library."""

    def __init__(self, dlpath: str):

        self.dlpath: str = dlpath
        self.devices: List[MockFLIDevice] = []

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

        device.prepare_image()  # Prepare image

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

    def _get_image(self, dev):
        """Return the whole image. Used for the ``fast_read`` mode."""

        device = self._get_device(dev)

        assert device is not None and device.image is not None

        image = device.image.copy()
        device.clear_image()

        return image

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

        assert device is not None and device.image is not None

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

        if device.image.shape[0] == device.row:
            device.clear_image()
        else:
            device.row += 1

        return self.restype(0)
