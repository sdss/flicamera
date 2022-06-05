#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: lib.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

# Heavily copied from Craig Wm. Versek's code at http://bit.ly/2M6ESHq.

from __future__ import annotations

import ctypes
import os
import pathlib
from ctypes import (
    POINTER,
    byref,
    c_char_p,
    c_double,
    c_int,
    c_long,
    c_size_t,
    c_ulong,
    c_void_p,
)

from typing import Dict, Optional, Tuple

import numpy


__ALL__ = ["LibFLI", "FLIWarning", "FLIError", "chk_err"]


c_double_p = POINTER(c_double)
c_long_p = POINTER(c_long)

FLI_INVALID_DEVICE = -1


flidev_t = c_long
flidomain_t = c_long

FLIDOMAIN_NONE = 0x00
FLIDOMAIN_PARALLEL_PORT = 0x01
FLIDOMAIN_USB = 0x02
FLIDOMAIN_SERIAL = 0x03
FLIDOMAIN_INET = 0x04
FLIDOMAIN_SERIAL_19200 = 0x05
FLIDOMAIN_SERIAL_1200 = 0x06

FLIDEVICE_NONE = 0x000
FLIDEVICE_CAMERA = 0x100
FLIDEVICE_FILTERWHEEL = 0x200
FLIDEVICE_FOCUSER = 0x300
FLIDEVICE_HS_FILTERWHEEL = 0x0400
FLIDEVICE_RAW = 0x0F00
FLIDEVICE_ENUMERATE_BY_CONNECTION = 0x8000


# The frame type for an FLI CCD camera device.

fliframe_t = c_long

FLI_FRAME_TYPE_NORMAL = 0
FLI_FRAME_TYPE_DARK = 1
FLI_FRAME_TYPE_FLOOD = 2
FLI_FRAME_TYPE_RBI_FLUSH = FLI_FRAME_TYPE_FLOOD | FLI_FRAME_TYPE_DARK


# The gray-scale bit depth for an FLI camera device.

flibitdepth_t = c_long

FLI_MODE_8BIT = flibitdepth_t(0)
FLI_MODE_16BIT = flibitdepth_t(1)


# Type used for shutter operations for an FLI camera device.

flishutter_t = c_long

FLI_SHUTTER_CLOSE = 0x0000
FLI_SHUTTER_OPEN = 0x0001
FLI_SHUTTER_EXTERNAL_TRIGGER = 0x0002
FLI_SHUTTER_EXTERNAL_TRIGGER_LOW = 0x0002
FLI_SHUTTER_EXTERNAL_TRIGGER_HIGH = 0x0004
FLI_SHUTTER_EXTERNAL_EXPOSURE_CONTROL = 0x0008


# Type used for background flush operations for an FLI camera device.

flibgflush_t = c_long

FLI_BGFLUSH_STOP = 0x0000
FLI_BGFLUSH_START = 0x0001


# Type used to determine which temperature channel to read.

flichannel_t = c_long

FLI_TEMPERATURE_INTERNAL = 0x0000
FLI_TEMPERATURE_EXTERNAL = 0x0001
FLI_TEMPERATURE_CCD = 0x0000
FLI_TEMPERATURE_BASE = 0x0001


# Type specifying library debug levels.

flidebug_t = c_long
flimode_t = c_long
flistatus_t = c_long
flitdirate_t = c_long
flitdiflags_t = c_long


# Status settings

FLI_CAMERA_STATUS_UNKNOWN = 0xFFFFFFFF
FLI_CAMERA_STATUS_MASK = 0x00000003
FLI_CAMERA_STATUS_IDLE = 0x00
FLI_CAMERA_STATUS_WAITING_FOR_TRIGGER = 0x01
FLI_CAMERA_STATUS_EXPOSING = 0x02
FLI_CAMERA_STATUS_READING_CCD = 0x03
FLI_CAMERA_DATA_READY = 0x80000000

FLI_FOCUSER_STATUS_UNKNOWN = 0xFFFFFFFF
FLI_FOCUSER_STATUS_HOMING = 0x00000004
FLI_FOCUSER_STATUS_MOVING_IN = 0x00000001
FLI_FOCUSER_STATUS_MOVING_OUT = 0x00000002
FLI_FOCUSER_STATUS_MOVING_MASK = 0x00000007
FLI_FOCUSER_STATUS_HOME = 0x00000080
FLI_FOCUSER_STATUS_LIMIT = 0x00000040
FLI_FOCUSER_STATUS_LEGACY = 0x10000000

FLI_FILTER_WHEEL_PHYSICAL = 0x100
FLI_FILTER_WHEEL_VIRTUAL = 0
FLI_FILTER_WHEEL_LEFT = FLI_FILTER_WHEEL_PHYSICAL | 0x00
FLI_FILTER_WHEEL_RIGHT = FLI_FILTER_WHEEL_PHYSICAL | 0x01
FLI_FILTER_STATUS_MOVING_CCW = 0x01
FLI_FILTER_STATUS_MOVING_CW = 0x02
FLI_FILTER_POSITION_UNKNOWN = 0xFF
FLI_FILTER_POSITION_CURRENT = 0x200
FLI_FILTER_STATUS_HOMING = 0x00000004
FLI_FILTER_STATUS_HOME = 0x00000080
FLI_FILTER_STATUS_HOME_LEFT = 0x00000080
FLI_FILTER_STATUS_HOME_RIGHT = 0x00000040
FLI_FILTER_STATUS_HOME_SUCCEEDED = 0x00000008

FLIDEBUG_NONE = 0x00
FLIDEBUG_INFO = 0x01
FLIDEBUG_WARN = 0x02
FLIDEBUG_FAIL = 0x04
FLIDEBUG_IO = 0x08
FLIDEBUG_ALL = FLIDEBUG_INFO | FLIDEBUG_WARN | FLIDEBUG_FAIL

FLI_IO_P0 = 0x01
FLI_IO_P1 = 0x02
FLI_IO_P2 = 0x04
FLI_IO_P3 = 0x08

FLI_FAN_SPEED_OFF = 0x00
FLI_FAN_SPEED_ON = 0xFFFFFFFF

FLI_EEPROM_USER = 0x00
FLI_EEPROM_PIXEL_MAP = 0x01

FLI_PIXEL_DEFECT_COLUMN = 0x00
FLI_PIXEL_DEFECT_CLUSTER = 0x10
FLI_PIXEL_DEFECT_POINT_BRIGHT = 0x20
FLI_PIXEL_DEFECT_POINT_DARK = 0x30


_API_FUNCTION_PROTOTYPES = [
    (
        "FLIOpen",
        [POINTER(flidev_t), c_char_p, flidomain_t],
    ),  # (flidev_t *dev, char *name, flidomain_t domain);
    ("FLIClose", [flidev_t]),  # (flidev_t dev);
    ("FLISetDebugLevel", [c_char_p, flidebug_t]),  # (char *host, flidebug_t level);
    ("FLIGetLibVersion", [c_char_p, c_size_t]),  # (char* ver, size_t len);
    (
        "FLIGetModel",
        [flidev_t, c_char_p, c_size_t],
    ),  # (flidev_t dev, char* model, size_t len);
    (
        "FLIGetArrayArea",
        [flidev_t, c_long_p, c_long_p, c_long_p, c_long_p],
    ),  # (flidev_t dev, long* ul_x, long* ul_y,long* lr_x, long* lr_y);
    (
        "FLIGetVisibleArea",
        [flidev_t, c_long_p, c_long_p, c_long_p, c_long_p],
    ),  # (flidev_t dev, long* ul_x, long* ul_y,long* lr_x, long* lr_y);
    ("FLIExposeFrame", [flidev_t]),  # (flidev_t dev);
    ("FLICancelExposure", [flidev_t]),  # (flidev_t dev);
    ("FLIGetExposureStatus", [flidev_t, c_long_p]),  # (flidev_t dev, long *timeleft);
    ("FLISetTemperature", [flidev_t, c_double]),  # (flidev_t dev, double temperature);
    (
        "FLIGetTemperature",
        [flidev_t, c_double_p],
    ),  # (flidev_t dev, double *temperature);
    (
        "FLIGrabRow",
        [flidev_t, c_void_p, c_size_t],
    ),  # (flidev_t dev, void *buff, size_t width);
    (
        "FLIGrabFrame",
        [flidev_t, c_void_p, c_size_t, POINTER(c_size_t)],
    ),  # (flidev_t dev, void* buff, size_t buffsize, size_t* bytesgrabbed);
    (
        "FLIFlushRow",
        [flidev_t, c_long, c_long],
    ),  # (flidev_t dev, long rows, long repeat);
    ("FLISetExposureTime", [flidev_t, c_long]),  # (flidev_t dev, long exptime);
    (
        "FLISetFrameType",
        [flidev_t, fliframe_t],
    ),  # (flidev_t dev, fliframe_t frametype);
    (
        "FLISetImageArea",
        [flidev_t, c_long, c_long, c_long, c_long],
    ),  # (flidev_t dev, long ul_x, long ul_y, long lr_x, long lr_y);
    ("FLISetHBin", [flidev_t, c_long]),  # (flidev_t dev, long hbin);
    ("FLISetVBin", [flidev_t, c_long]),  # (flidev_t dev, long vbin);
    ("FLISetNFlushes", [flidev_t, c_long]),  # (flidev_t dev, long nflushes);
    (
        "FLISetBitDepth",
        [flidev_t, flibitdepth_t],
    ),  # (flidev_t dev, flibitdepth_t bitdepth);
    ("FLIReadIOPort", [flidev_t, c_long_p]),  # (flidev_t dev, long *ioportset);
    ("FLIWriteIOPort", [flidev_t, c_long]),  # (flidev_t dev, long ioportset);
    ("FLIConfigureIOPort", [flidev_t, c_long]),  # (flidev_t dev, long ioportset);
    (
        "FLIControlShutter",
        [flidev_t, flishutter_t],
    ),  # (flidev_t dev, flishutter_t shutter);
    ("FLILockDevice", [flidev_t]),  # (flidev_t dev);
    ("FLIUnlockDevice", [flidev_t]),  # (flidev_t dev);
    (
        "FLIList",
        [flidomain_t, POINTER(POINTER(c_char_p))],
    ),  # (flidomain_t domain, char ***names);
    ("FLIFreeList", [POINTER(c_char_p)]),  # (char **names);
    ("FLISetFilterPos", [flidev_t, c_long]),  # (flidev_t dev, long filter);
    ("FLIGetFilterPos", [flidev_t, c_long_p]),  # (flidev_t dev, long *filter);
    ("FLIGetFilterCount", [flidev_t, c_long_p]),  # (flidev_t dev, long *filter);
    ("FLIStepMotor", [flidev_t, c_long]),  # (flidev_t dev, long steps);
    ("FLIGetStepperPosition", [flidev_t, c_long_p]),  # (flidev_t dev, long *position);
    ("FLIGetHWRevision", [flidev_t, c_long_p]),  # (flidev_t dev, long *hwrev);
    (
        "FLIGetPixelSize",
        [flidev_t, c_double_p, c_double_p],
    ),  # (flidev_t dev, double *pixel_x, double *pixel_y);
    ("FLIGetFWRevision", [flidev_t, c_long_p]),  # (flidev_t dev, long *fwrev);
    ("FLIHomeFocuser", [flidev_t]),  # (flidev_t dev);
    ("FLICreateList", [flidomain_t]),  # (flidomain_t domain);
    ("FLIDeleteList", []),  # (void);
    (
        "FLIListFirst",
        [POINTER(flidomain_t), c_char_p, c_size_t, c_char_p, c_size_t],
    ),  # (flidomain_t *domain, char *filename,size_t fnlen, char *name, size_t namelen);
    (
        "FLIListNext",
        [POINTER(flidomain_t), c_char_p, c_size_t, c_char_p, c_size_t],
    ),  # (flidomain_t *domain, char *filename,size_t fnlen, char *name, size_t namelen);
    (
        "FLIControlBackgroundFlush",
        [flidev_t, flibgflush_t],
    ),  # (flidev_t dev, flibgflush_t bgflush);
    ("FLISetDAC", [flidev_t, c_ulong]),  # (flidev_t dev, unsigned long dacset);
    ("FLIGetStepsRemaining", [flidev_t, c_long_p]),  # (flidev_t dev, long *steps);
    ("FLIStepMotorAsync", [flidev_t, c_long]),  # (flidev_t dev, long steps);
    (
        "FLIReadTemperature",
        [flidev_t, flichannel_t, c_double_p],
    ),  # (flidev_t dev,flichannel_t channel, double *temperature);
    ("FLIGetFocuserExtent", [flidev_t, c_long_p]),  # (flidev_t dev, long *extent);
    (
        "FLIUsbBulkIO",
        [flidev_t, c_int, c_void_p, c_long_p],
    ),  # (flidev_t dev, int ep, void *buf, long *len);
    ("FLIGetCoolerPower", [flidev_t, c_double_p]),  # (flidev_t dev, double *power);
    ("FLIGetDeviceStatus", [flidev_t, c_long_p]),  # (flidev_t dev, long *status);
    (
        "FLIGetCameraModeString",
        [flidev_t, flimode_t, c_char_p, c_size_t],
    ),  # (flidev_t dev, flimode_t mode_index, char *mode_string, size_t siz);
    (
        "FLIGetCameraMode",
        [flidev_t, POINTER(flimode_t)],
    ),  # (flidev_t dev, flimode_t *mode_index);
    (
        "FLISetCameraMode",
        [flidev_t, flimode_t],
    ),  # (flidev_t dev, flimode_t mode_index);
    ("FLIHomeDevice", [flidev_t]),  # (flidev_t dev);
    (
        "FLIGrabVideoFrame",
        [flidev_t, c_void_p, c_size_t],
    ),  # (flidev_t dev, void *buff, size_t size);
    ("FLIStopVideoMode", [flidev_t]),  # (flidev_t dev);
    ("FLIStartVideoMode", [flidev_t]),  # (flidev_t dev);
    (
        "FLIGetSerialString",
        [flidev_t, c_char_p, c_size_t],
    ),  # (flidev_t dev, char* serial, size_t len);
    ("FLIEndExposure", [flidev_t]),  # (flidev_t dev);
    ("FLITriggerExposure", [flidev_t]),  # (flidev_t dev);
    ("FLISetFanSpeed", [flidev_t, c_long]),  # (flidev_t dev, long fan_speed);
    (
        "FLISetVerticalTableEntry",
        [flidev_t, c_long, c_long, c_long, c_long],
    ),  # (flidev_t dev, long index, long height, long bin, long mode);
    (
        "FLIGetVerticalTableEntry",
        [flidev_t, c_long, c_long_p, c_long_p, c_long_p],
    ),  # (flidev_t dev, long index, long *height, long *bin, long *mode);
    (
        "FLIGetReadoutDimensions",
        [flidev_t, c_long_p, c_long_p, c_long_p, c_long_p, c_long_p, c_long_p],
    ),  # (flidev_t dev, long *width, long *hoffset, long *hbin, long *height, long *voffset, long *vbin);
    (
        "FLIEnableVerticalTable",
        [flidev_t, c_long, c_long, c_long],
    ),  # (flidev_t dev, long width, long offset, long flags);
    (
        "FLIReadUserEEPROM",
        [flidev_t, c_long, c_long, c_long, c_void_p],
    ),  # (flidev_t dev, long loc, long address, long length, void *rbuf);
    (
        "FLIWriteUserEEPROM",
        [flidev_t, c_long, c_long, c_long, c_void_p],
    ),  # (flidev_t dev, long loc, long address, long length, void *wbuf);
    ("FLISetActiveWheel", [flidev_t, c_long]),  # (flidev_t dev, long wheel);
    (
        "FLIGetFilterName",
        [flidev_t, c_long, c_char_p, c_size_t],
    ),  # (flidev_t dev, long filter, char *name, size_t len);
    (
        "FLISetTDI",
        [flidev_t, flitdirate_t, flitdiflags_t],
    ),  # (flidev_t dev, flitdirate_t tdi_rate, flitdiflags_t flags);
]


def chk_err(err):
    """Wraps a libFLI C function call with error checking code."""
    if err < 0:
        msg = os.strerror(abs(err))  # err is always negative
        raise FLIError(msg + f" ({err})")
    if err > 0:
        msg = os.strerror(err)
        raise FLIWarning(msg + f" ({err})")
    return err


class FLIWarning(UserWarning):
    """A warning from the FLI library."""

    pass


class FLIError(Exception):
    """An error from the FLI library."""

    pass


class LibFLI(ctypes.CDLL):
    """Wrapper for the FLI library.

    Parameters
    ----------
    shared_object
        The path to the FLI library shared object. If not provided, uses the
        default, internal version.
    debug
        Whether to use the debug mode.

    """

    def __init__(
        self,
        shared_object: Optional[str] = None,
        debug: bool = False,
        simulation_mode: bool = False,
    ):

        self.domain = flidomain_t(FLIDOMAIN_USB | FLIDEVICE_CAMERA)

        if not shared_object:
            if not simulation_mode:  # pragma: no cover
                workdir = pathlib.Path(__file__).parent
                shared_object_list = list(workdir.glob("libfli*.so"))
                if len(shared_object_list) == 0:
                    raise OSError("The library was compiled without a copy of libfli.")
                shared_object = str(shared_object_list[0])
            else:
                shared_object = "libflimock.so"

        self.libc = ctypes.cdll.LoadLibrary(shared_object)

        if self.libc is None:
            raise RuntimeError("Cannot load the libfli shared library.")

        # Sets the argtypes and restype.
        for funcname, argtypes in _API_FUNCTION_PROTOTYPES:
            so_func = self.libc.__getattr__(funcname)
            so_func.argtypes = argtypes
            so_func.restype = chk_err

        if debug:
            self.set_debug(True)

    @staticmethod
    def _convert_to_list(ptr):

        if not ptr:
            return []

        list_ = []
        ii = 0
        while ptr[ii]:
            list_.append(ptr[ii].decode().split(";")[0])
            ii += 1

        return list_

    def set_debug(self, debug=True):
        """Turns the debug system on/off."""

        debug_level = flidebug_t(FLIDEBUG_ALL if debug else FLIDEBUG_NONE)
        self.libc.FLISetDebugLevel(c_char_p(None), debug_level)

    def list_cameras(self):
        """Returns a list of connected camera names."""

        names_ptr = POINTER(ctypes.c_char_p)()
        self.libc.FLIList(self.domain, byref(names_ptr))

        cameras = self._convert_to_list(names_ptr)

        # Free the list
        if names_ptr:
            self.libc.FLIFreeList(names_ptr)

        return cameras

    def get_camera(self, serial):
        """Gets a camera by its serial string."""

        camera_names = self.list_cameras()
        for camera_name in camera_names:
            fli_camera = LibFLIDevice(camera_name, self.libc)
            if fli_camera.serial == serial:
                return fli_camera

        return None


class LibFLIDevice(object):
    """A FLI device."""

    _instances = {}

    def __new__(cls, name, libc):

        # Create a singleton to avoid opening the camera multiple times.
        if name not in cls._instances:
            cls._instances[name] = super(LibFLIDevice, cls).__new__(cls)
            cls._instances[name].is_open = False

        return cls._instances[name]

    def __init__(self, name, libc):

        if not self.is_open:

            self.domain = flidomain_t(FLIDOMAIN_USB | FLIDEVICE_CAMERA)
            self._str_size = 100

            self.name = name if isinstance(name, str) else name.decode()
            self.libc = libc

            self.dev = flidev_t()
            self._model = ctypes.create_string_buffer(self._str_size)
            self._serial = ctypes.create_string_buffer(self._str_size)

            self.fwrev: int
            self.hwrev: int

            self.hbin: int
            self.vbin: int

            # The image area (ul_x, ul_y, lr_x, lr_y)
            self.area: Tuple[int, int, int, int]

            self.shutter = False
            self._temperature: Dict[str, float] = {"CCD": 0.0, "base": 0.0}

            self.open()

    @property
    def model(self):
        """The model of the device."""

        return self._model.value.decode()

    @property
    def serial(self):
        """The serial string of the device."""

        return self._serial.value.decode()

    @property
    def temperature(self):
        """Returns a dictionary of temperatures at different locations."""

        self._update_temperature()

        return self._temperature

    def open(self):
        """Opens the device and grabs information."""

        self.libc.FLIOpen(byref(self.dev), self.name.encode(), self.domain)
        self.libc.FLILockDevice(self.dev)

        fwrev = c_long()
        self.libc.FLIGetFWRevision(self.dev, byref(fwrev))
        self.fwrev = fwrev.value

        hwrev = c_long()
        self.libc.FLIGetHWRevision(self.dev, byref(hwrev))
        self.hwrev = hwrev.value

        self.libc.FLIGetModel(self.dev, self._model, self._str_size)
        self.libc.FLIGetSerialString(self.dev, self._serial, self._str_size)

        # The camera doesn't allow to get the status of the shutter so we
        # close it on initialisation to be sure we know where it is.
        self.set_shutter(False)

        # Set bit depth (all our cameras should support 16bits)
        # self.libc.FLISetBitDepth(self.dev, FLI_MODE_16BIT)

        self._update_temperature()

        # Sets the binning to (1, 1) and resets the image area.
        self.set_binning(1, 1)

        self.is_open = True

    def __del__(self):
        """Closes the device."""

        self.libc.FLIUnlockDevice(self.dev)

        if self.is_open:
            self.libc.FLIClose(self.dev)

    def _update_temperature(self):
        """Gets the temperatures and updates the ``temperature`` dict."""

        temp = c_double()

        self.libc.FLIReadTemperature(self.dev, FLI_TEMPERATURE_BASE, byref(temp))
        self._temperature["base"] = temp.value

        self.libc.FLIReadTemperature(self.dev, FLI_TEMPERATURE_CCD, byref(temp))
        self._temperature["CCD"] = temp.value

    def set_temperature(self, temp: float):
        """Sets the temperature of the CCD.

        Parameters
        ----------
        temp
            Temperature in the range -55 to 45C.
        """

        self.libc.FLISetTemperature(self.dev, c_double(temp))

    def set_shutter(self, shutter_value: bool):
        """Controls the shutter of the camera.

        Parameters
        ----------
        shutter_value
            If `True`, opens the shutter, otherwise closes it.
        """

        shutter_flag = FLI_SHUTTER_OPEN if shutter_value else FLI_SHUTTER_CLOSE

        self.libc.FLIControlShutter(self.dev, shutter_flag)

        self.shutter = shutter_value

    def get_cooler_power(self):
        """Returns the cooler power."""

        cooler = c_double()
        self.libc.FLIGetCoolerPower(self.dev, byref(cooler))

        return cooler.value

    def set_exposure_time(self, exp_time: float):
        """Sets the exposure time.

        Parameters
        ----------
        exp_time
            The exposure time, in seconds.
        """

        self.libc.FLISetExposureTime(self.dev, int(exp_time * 1000.0))

    def set_image_area(self, area: Optional[Tuple[int, int, int, int]] = None):
        r"""Sets the area of the image to exposure.

        Parameters
        ----------
        area : tuple
            The area in the format :math:`(ul_x, ul_y, lr_x, lr_y)` where
            :math:`ul` refers to the upper-left corner of the CCD, and
            :math:`lr` to the lower right. The lower-right values to pass
            must take into account the horizontal and vertical binning factors.
            In practice one must pass :math:`lr_x^\prime` and
            :math:`lr_y^\prime` defined as

            .. math::

                lr_x^\prime = ul_x + (lr_x - ul_x) / hbin \\
                lr_y^\prime = ul_y + (lr_y - ul_y) / vbin

            If you pass the area, it is assumed that you are using the full
            image area as reference; the binning is automatically taken into
            account. Although the visible area does not necessary start at
            ``(0, 0)``, the area passed to this function should assume an
            origin at ``(0, 0)``. If ``area`` is `None`, the full area of
            the chip is used, using the current binning.

        """

        assert self.hbin and self.vbin, "set the binning before the area."

        v_ul_x, v_ul_y, v_lr_x, v_lr_y = self.get_visible_area()

        if area:

            ul_x = v_ul_x + area[0]
            ul_y = v_ul_y + area[1]
            lr_x = v_ul_x + area[2]
            lr_y = v_ul_y + area[3]

        else:

            ul_x = v_ul_x
            ul_y = v_ul_y
            lr_x = v_lr_x
            lr_y = v_lr_y

        lr_x_prime = int(ul_x + (lr_x - ul_x) / self.hbin)
        lr_y_prime = int(ul_y + (lr_y - ul_y) / self.vbin)

        self.libc.FLISetImageArea(self.dev, ul_x, ul_y, lr_x_prime, lr_y_prime)

        self.area = (ul_x - v_ul_x, ul_y - v_ul_y, lr_x - v_ul_x, lr_y - v_ul_y)

    def get_visible_area(self) -> Tuple[int, int, int, int]:
        """Returns the visible area.

        Returns
        -------
        visible_area
            The visible area in the format :math:`(ul_x, ul_y, lr_x, lr_y)`.
            See `.set_image_area` for details. The visible area does not change
            regardless of the binning or image area defined; it's the total
            available area. Note that :math:`lr_x-ul_x` and :math:`lr_y-ul_y`
            match the total size of the CCD, but :math:`lr_x` or :math:`lr_y`
            are not necessarily zero.
        """

        ul_x = c_long()
        ul_y = c_long()
        lr_x = c_long()
        lr_y = c_long()

        self.libc.FLIGetVisibleArea(
            self.dev, byref(ul_x), byref(ul_y), byref(lr_x), byref(lr_y)
        )

        return (ul_x.value, ul_y.value, lr_x.value, lr_y.value)

    def set_binning(self, hbin, vbin):
        """Sets the binning.

        The image area is automatically re-adjusted to be the full visible
        area. If you want to change this, use `.set_image_area` manually.

        """

        assert hbin >= 1 and hbin <= 16, "invalid hbin value."
        assert int(hbin) == hbin, "hbin is not an integer"

        assert vbin >= 1 and vbin <= 16, "invalid vbin value."
        assert int(vbin) == vbin, "vbin is not an integer"

        self.libc.FLISetHBin(self.dev, c_long(hbin))
        self.libc.FLISetVBin(self.dev, c_long(vbin))

        self.hbin = hbin
        self.vbin = vbin

        # Sets the image area. Passing it without arguments it uses the full
        # visible area but takes into account the just set binning values.
        self.set_image_area()

    def get_exposure_time_left(self):
        """Returns the remaining exposure time, in milliseconds.."""

        timeleft = c_long()
        self.libc.FLIGetExposureStatus(self.dev, byref(timeleft))

        return timeleft.value

    def cancel_exposure(self):
        """Cancels an exposure."""

        self.libc.FLICancelExposure(self.dev)

    def start_exposure(self, frametype="normal"):
        """Starts and exposure and returns immediately."""

        if frametype == "dark":
            frametype = FLI_FRAME_TYPE_DARK
        else:
            frametype = FLI_FRAME_TYPE_NORMAL

        self.libc.FLISetFrameType(self.dev, fliframe_t(frametype))
        self.libc.FLISetTDI(self.dev, 0, 0)
        self.libc.FLIExposeFrame(self.dev)

    def read_frame(self):
        """Reads the image frame.

        This function reads the image buffer row by row. In principle it could
        be optimised by writing a C function to encapsulate the loop, but tests
        show that the gain is marginal so it's ok to keep it as a pure Python
        method.

        """

        if self.get_exposure_time_left() > 0:
            raise FLIError("the camera is still exposing.")

        (ul_x, ul_y, lr_x, lr_y) = self.area

        n_cols = int((lr_x - ul_x) / self.hbin)
        n_rows = int((lr_y - ul_y) / self.vbin)

        array = numpy.empty((n_rows, n_cols), dtype=numpy.uint16)

        img_ptr = array.ctypes.data_as(POINTER(ctypes.c_uint16))

        for row in range(n_rows):
            offset = row * n_cols * ctypes.sizeof(ctypes.c_uint16)
            self.libc.FLIGrabRow(self.dev, byref(img_ptr.contents, offset), n_cols)

        return array
