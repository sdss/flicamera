#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: lib.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

# Heavily copied from Craig Wm. Versek's code at http://bit.ly/2M6ESHq.

import ctypes
import os
import pathlib
from ctypes import POINTER, c_char_p, c_double, c_int, c_long, c_size_t, c_ulong, c_void_p


__ALL__ = ['LibFLI', 'FLIWarning', 'FLIError', 'chk_err']


c_double_p = POINTER(c_double)
c_long_p = POINTER(c_long)

FLI_INVALID_DEVICE = -1


flidev_t = c_long
flidomain_t = c_long

FLIDOMAIN_NONE           = 0x00
FLIDOMAIN_PARALLEL_PORT  = 0x01
FLIDOMAIN_USB            = 0x02
FLIDOMAIN_SERIAL         = 0x03
FLIDOMAIN_INET           = 0x04
FLIDOMAIN_SERIAL_19200   = 0x05
FLIDOMAIN_SERIAL_1200    = 0x06

FLIDEVICE_NONE                    = 0x000
FLIDEVICE_CAMERA                  = 0x100
FLIDEVICE_FILTERWHEEL             = 0x200
FLIDEVICE_FOCUSER                 = 0x300
FLIDEVICE_HS_FILTERWHEEL          = 0x0400
FLIDEVICE_RAW                     = 0x0f00
FLIDEVICE_ENUMERATE_BY_CONNECTION = 0x8000


# The frame type for an FLI CCD camera device.

fliframe_t = c_long

FLI_FRAME_TYPE_NORMAL = 0
FLI_FRAME_TYPE_DARK   = 1
FLI_FRAME_TYPE_FLOOD  = 2
FLI_FRAME_TYPE_RBI_FLUSH = FLI_FRAME_TYPE_FLOOD | FLI_FRAME_TYPE_DARK

# The gray-scale bit depth for an FLI camera device.

flibitdepth_t = c_long

FLI_MODE_8BIT  = flibitdepth_t(0)
FLI_MODE_16BIT = flibitdepth_t(1)


# Type used for shutter operations for an FLI camera device.

flishutter_t = c_long

FLI_SHUTTER_CLOSE                     = 0x0000
FLI_SHUTTER_OPEN                      = 0x0001
FLI_SHUTTER_EXTERNAL_TRIGGER          = 0x0002
FLI_SHUTTER_EXTERNAL_TRIGGER_LOW      = 0x0002
FLI_SHUTTER_EXTERNAL_TRIGGER_HIGH     = 0x0004
FLI_SHUTTER_EXTERNAL_EXPOSURE_CONTROL = 0x0008


# Type used for background flush operations for an FLI camera device.

flibgflush_t = c_long

FLI_BGFLUSH_STOP  = 0x0000
FLI_BGFLUSH_START = 0x0001


# Type used to determine which temperature channel to read.

flichannel_t = c_long

FLI_TEMPERATURE_INTERNAL = 0x0000
FLI_TEMPERATURE_EXTERNAL = 0x0001
FLI_TEMPERATURE_CCD      = 0x0000
FLI_TEMPERATURE_BASE     = 0x0001


# Type specifying library debug levels.

flidebug_t    = c_long
flimode_t     = c_long
flistatus_t   = c_long
flitdirate_t  = c_long
flitdiflags_t = c_long


# Status settings

FLI_CAMERA_STATUS_UNKNOWN             = 0xffffffff
FLI_CAMERA_STATUS_MASK                = 0x00000003
FLI_CAMERA_STATUS_IDLE                = 0x00
FLI_CAMERA_STATUS_WAITING_FOR_TRIGGER = 0x01
FLI_CAMERA_STATUS_EXPOSING            = 0x02
FLI_CAMERA_STATUS_READING_CCD         = 0x03
FLI_CAMERA_DATA_READY                 = 0x80000000

FLI_FOCUSER_STATUS_UNKNOWN     = 0xffffffff
FLI_FOCUSER_STATUS_HOMING      = 0x00000004
FLI_FOCUSER_STATUS_MOVING_IN   = 0x00000001
FLI_FOCUSER_STATUS_MOVING_OUT  = 0x00000002
FLI_FOCUSER_STATUS_MOVING_MASK = 0x00000007
FLI_FOCUSER_STATUS_HOME        = 0x00000080
FLI_FOCUSER_STATUS_LIMIT       = 0x00000040
FLI_FOCUSER_STATUS_LEGACY      = 0x10000000

FLI_FILTER_WHEEL_PHYSICAL        = 0x100
FLI_FILTER_WHEEL_VIRTUAL         = 0
FLI_FILTER_WHEEL_LEFT            = FLI_FILTER_WHEEL_PHYSICAL | 0x00
FLI_FILTER_WHEEL_RIGHT           = FLI_FILTER_WHEEL_PHYSICAL | 0x01
FLI_FILTER_STATUS_MOVING_CCW     = 0x01
FLI_FILTER_STATUS_MOVING_CW      = 0x02
FLI_FILTER_POSITION_UNKNOWN      = 0xff
FLI_FILTER_POSITION_CURRENT      = 0x200
FLI_FILTER_STATUS_HOMING         = 0x00000004
FLI_FILTER_STATUS_HOME           = 0x00000080
FLI_FILTER_STATUS_HOME_LEFT      = 0x00000080
FLI_FILTER_STATUS_HOME_RIGHT     = 0x00000040
FLI_FILTER_STATUS_HOME_SUCCEEDED = 0x00000008

FLIDEBUG_NONE = 0x00
FLIDEBUG_INFO = 0x01
FLIDEBUG_WARN = 0x02
FLIDEBUG_FAIL = 0x04
FLIDEBUG_IO   = 0x08
FLIDEBUG_ALL  = FLIDEBUG_INFO | FLIDEBUG_WARN | FLIDEBUG_FAIL

FLI_IO_P0 = 0x01
FLI_IO_P1 = 0x02
FLI_IO_P2 = 0x04
FLI_IO_P3 = 0x08

FLI_FAN_SPEED_OFF = 0x00
FLI_FAN_SPEED_ON  = 0xffffffff

FLI_EEPROM_USER      = 0x00
FLI_EEPROM_PIXEL_MAP = 0x01

FLI_PIXEL_DEFECT_COLUMN       = 0x00
FLI_PIXEL_DEFECT_CLUSTER      = 0x10
FLI_PIXEL_DEFECT_POINT_BRIGHT = 0x20
FLI_PIXEL_DEFECT_POINT_DARK   = 0x30


_API_FUNCTION_PROTOTYPES = [
    ('FLIOpen', [POINTER(flidev_t), c_char_p, flidomain_t]),  # (flidev_t *dev, char *name, flidomain_t domain);
    ('FLIClose', [flidev_t]),                                 # (flidev_t dev);
    ('FLISetDebugLevel', [c_char_p, flidebug_t]),             # (char *host, flidebug_t level);
    ('FLIGetLibVersion', [c_char_p, c_size_t]),               # (char* ver, size_t len);
    ('FLIGetModel', [flidev_t, c_char_p, c_size_t]),          # (flidev_t dev, char* model, size_t len);
    ('FLIGetArrayArea', [flidev_t,
                         c_long_p,
                         c_long_p,
                         c_long_p,
                         c_long_p]),                          # (flidev_t dev, long* ul_x, long* ul_y,long* lr_x, long* lr_y);
    ('FLIGetVisibleArea', [flidev_t,
                           c_long_p,
                           c_long_p,
                           c_long_p,
                           c_long_p]),                        # (flidev_t dev, long* ul_x, long* ul_y,long* lr_x, long* lr_y);
    ('FLIExposeFrame', [flidev_t]),                           # (flidev_t dev);
    ('FLICancelExposure', [flidev_t]),                        # (flidev_t dev);
    ('FLIGetExposureStatus', [flidev_t, c_long_p]),           # (flidev_t dev, long *timeleft);
    ('FLISetTemperature', [flidev_t, c_double]),              # (flidev_t dev, double temperature);
    ('FLIGetTemperature', [flidev_t, c_double_p]),            # (flidev_t dev, double *temperature);
    ('FLIGrabRow', [flidev_t, c_void_p, c_size_t]),           # (flidev_t dev, void *buff, size_t width);
    ('FLIGrabFrame', [flidev_t,
                      c_void_p,
                      c_size_t,
                      POINTER(c_size_t)]),                    # (flidev_t dev, void* buff, size_t buffsize, size_t* bytesgrabbed);
    ('FLIFlushRow', [flidev_t, c_long, c_long]),              # (flidev_t dev, long rows, long repeat);
    ('FLISetExposureTime', [flidev_t, c_long]),               # (flidev_t dev, long exptime);
    ('FLISetFrameType', [flidev_t, fliframe_t]),              # (flidev_t dev, fliframe_t frametype);
    ('FLISetImageArea', [flidev_t,
                         c_long,
                         c_long,
                         c_long,
                         c_long]),                            # (flidev_t dev, long ul_x, long ul_y, long lr_x, long lr_y);
    ('FLISetHBin', [flidev_t, c_long]),                       # (flidev_t dev, long hbin);
    ('FLISetVBin', [flidev_t, c_long]),                       # (flidev_t dev, long vbin);
    ('FLISetNFlushes', [flidev_t, c_long]),                   # (flidev_t dev, long nflushes);
    ('FLISetBitDepth', [flidev_t, flibitdepth_t]),            # (flidev_t dev, flibitdepth_t bitdepth);
    ('FLIReadIOPort', [flidev_t, c_long_p]),                  # (flidev_t dev, long *ioportset);
    ('FLIWriteIOPort', [flidev_t, c_long]),                   # (flidev_t dev, long ioportset);
    ('FLIConfigureIOPort', [flidev_t, c_long]),               # (flidev_t dev, long ioportset);
    ('FLIControlShutter', [flidev_t, flishutter_t]),          # (flidev_t dev, flishutter_t shutter);
    ('FLILockDevice', [flidev_t]),                            # (flidev_t dev);
    ('FLIUnlockDevice', [flidev_t]),                          # (flidev_t dev);
    ('FLIList', [flidomain_t,
                 POINTER(POINTER(c_char_p))]),                # (flidomain_t domain, char ***names);
    ('FLIFreeList', [POINTER(c_char_p)]),                     # (char **names);
    ('FLISetFilterPos', [flidev_t, c_long]),                  # (flidev_t dev, long filter);
    ('FLIGetFilterPos', [flidev_t, c_long_p]),                # (flidev_t dev, long *filter);
    ('FLIGetFilterCount', [flidev_t, c_long_p]),              # (flidev_t dev, long *filter);
    ('FLIStepMotor', [flidev_t, c_long]),                     # (flidev_t dev, long steps);
    ('FLIGetStepperPosition', [flidev_t, c_long_p]),          # (flidev_t dev, long *position);
    ('FLIGetHWRevision', [flidev_t, c_long_p]),               # (flidev_t dev, long *hwrev);
    ('FLIGetPixelSize', [flidev_t, c_double_p, c_double_p]),  # (flidev_t dev, double *pixel_x, double *pixel_y);
    ('FLIGetFWRevision', [flidev_t, c_long_p]),               # (flidev_t dev, long *fwrev);
    ('FLIHomeFocuser', [flidev_t]),                           # (flidev_t dev);
    ('FLICreateList', [flidomain_t]),                         # (flidomain_t domain);
    ('FLIDeleteList', []),                                    # (void);
    ('FLIListFirst', [POINTER(flidomain_t),
                      c_char_p,
                      c_size_t,
                      c_char_p,
                      c_size_t]),                             # (flidomain_t *domain, char *filename,size_t fnlen, char *name, size_t namelen);
    ('FLIListNext', [POINTER(flidomain_t),
                     c_char_p,
                     c_size_t,
                     c_char_p,
                     c_size_t]),                              # (flidomain_t *domain, char *filename,size_t fnlen, char *name, size_t namelen);
    ('FLIControlBackgroundFlush', [flidev_t, flibgflush_t]),  # (flidev_t dev, flibgflush_t bgflush);
    ('FLISetDAC', [flidev_t, c_ulong]),                       # (flidev_t dev, unsigned long dacset);
    ('FLIGetStepsRemaining', [flidev_t, c_long_p]),           # (flidev_t dev, long *steps);
    ('FLIStepMotorAsync', [flidev_t, c_long]),                # (flidev_t dev, long steps);
    ('FLIReadTemperature', [flidev_t,
                            flichannel_t,
                            c_double_p]),                     # (flidev_t dev,flichannel_t channel, double *temperature);
    ('FLIGetFocuserExtent', [flidev_t, c_long_p]),            # (flidev_t dev, long *extent);
    ('FLIUsbBulkIO', [flidev_t, c_int, c_void_p, c_long_p]),  # (flidev_t dev, int ep, void *buf, long *len);
    ('FLIGetCoolerPower', [flidev_t, c_double_p]),            # (flidev_t dev, double *power);
    ('FLIGetDeviceStatus', [flidev_t, c_long_p]),             # (flidev_t dev, long *status);
    ('FLIGetCameraModeString', [flidev_t,
                                flimode_t,
                                c_char_p,
                                c_size_t]),                   # (flidev_t dev, flimode_t mode_index, char *mode_string, size_t siz);
    ('FLIGetCameraMode', [flidev_t, POINTER(flimode_t)]),     # (flidev_t dev, flimode_t *mode_index);
    ('FLISetCameraMode', [flidev_t, flimode_t]),              # (flidev_t dev, flimode_t mode_index);
    ('FLIHomeDevice', [flidev_t]),                            # (flidev_t dev);
    ('FLIGrabVideoFrame', [flidev_t, c_void_p, c_size_t]),    # (flidev_t dev, void *buff, size_t size);
    ('FLIStopVideoMode', [flidev_t]),                         # (flidev_t dev);
    ('FLIStartVideoMode', [flidev_t]),                        # (flidev_t dev);
    ('FLIGetSerialString', [flidev_t, c_char_p, c_size_t]),   # (flidev_t dev, char* serial, size_t len);
    ('FLIEndExposure', [flidev_t]),                           # (flidev_t dev);
    ('FLITriggerExposure', [flidev_t]),                       # (flidev_t dev);
    ('FLISetFanSpeed', [flidev_t, c_long]),                   # (flidev_t dev, long fan_speed);
    ('FLISetVerticalTableEntry', [flidev_t,
                                  c_long,
                                  c_long,
                                  c_long,
                                  c_long]),                   # (flidev_t dev, long index, long height, long bin, long mode);
    ('FLIGetVerticalTableEntry', [flidev_t,
                                  c_long,
                                  c_long_p,
                                  c_long_p,
                                  c_long_p]),                 # (flidev_t dev, long index, long *height, long *bin, long *mode);
    ('FLIGetReadoutDimensions', [flidev_t,
                                 c_long_p,
                                 c_long_p,
                                 c_long_p,
                                 c_long_p,
                                 c_long_p,
                                 c_long_p]),                  # (flidev_t dev, long *width, long *hoffset, long *hbin, long *height, long *voffset, long *vbin);
    ('FLIEnableVerticalTable', [flidev_t,
                                c_long,
                                c_long,
                                c_long]),                     # (flidev_t dev, long width, long offset, long flags);
    ('FLIReadUserEEPROM', [flidev_t,
                           c_long,
                           c_long,
                           c_long,
                           c_void_p]),                        # (flidev_t dev, long loc, long address, long length, void *rbuf);
    ('FLIWriteUserEEPROM', [flidev_t,
                            c_long,
                            c_long,
                            c_long,
                            c_void_p]),                       # (flidev_t dev, long loc, long address, long length, void *wbuf);
    ('FLISetActiveWheel', [flidev_t, c_long]),                # (flidev_t dev, long wheel);
    ('FLIGetFilterName', [flidev_t,
                          c_long,
                          c_char_p,
                          c_size_t]),                         # (flidev_t dev, long filter, char *name, size_t len);
    ('FLISetTDI', [flidev_t, flitdirate_t, flitdiflags_t]),   # (flidev_t dev, flitdirate_t tdi_rate, flitdiflags_t flags);
]


def chk_err(err):
    """Wraps a libFLI C function call with error checking code."""
    if err < 0:
        msg = os.strerror(abs(err))  # err is always negative
        raise FLIError(msg + f' ({err})')
    if err > 0:
        msg = os.strerror(err)
        raise FLIWarning(msg + f' ({err})')
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
    shared_object : str
        The path to the FLI library shared object. If not provided, uses the
        default, internal version.
    debug : bool
        Whether to use the debug mode.

    """

    def __new__(cls, shared_object=None, **kwargs):

        me = None

        if not shared_object:
            shared_object = list(pathlib.Path(__file__).parent.glob('libfli*.so'))
            if len(shared_object) == 0:
                raise RuntimeError('cannot find FLI library shared object.')
            shared_object.append('libfli.so')  # In case the library exists in a system location;.
        else:
            if not isinstance(shared_object, (list, tuple)):
                shared_object = [shared_object]

        for so in shared_object:
            try:
                me = ctypes.cdll.LoadLibrary(so)
                break
            except OSError:
                pass

        if me is None:
            raise RuntimeError('cannot load any of the provided shared libraries.')

        # A hack so to override the class of the returned object (CDLL) with
        # this class. It should be ok.
        me.__class__ = cls

        return me

    def __init__(self, shared_object=None, debug=False):

        # Sets the argtypes and restype.
        for funcname, argtypes in _API_FUNCTION_PROTOTYPES:
            so_func = self.__getattr__(funcname)
            so_func.argtypes = argtypes
            so_func.restype = chk_err

        if debug:
            self.set_debug(True)

    def call_function(self, funcname, *args):
        """Calls a FLI library function with arguments."""

        so_func = self.__getattr__(funcname)
        return so_func(*args)

    def set_debug(self, debug=True):
        """Turns the debug system on/off."""

        debug_level = flidebug_t(FLIDEBUG_ALL if debug else FLIDEBUG_NONE)
        self.FLISetDebugLevel(c_char_p(None), debug_level)

    def list_cameras(self):
        """Returns a list of connected cameras."""

        cameras = ctypes.POINTER(ctypes.c_char_p)()
        self.FLIList(flidomain_t(FLIDOMAIN_USB), ctypes.byref(cameras))

        return cameras
