#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: test_lib.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import time

import pytest

import flicamera.lib


def test_libfi_load(libfli):

    assert isinstance(libfli, flicamera.lib.LibFLI)

    # Test the mocking
    assert len(libfli.libc.devices) > 0


def test_list_cameras(libfli):

    assert len(libfli.list_cameras()) > 0


def test_get_camera(libfli, config):

    cameras_dict = config['cameras']

    for camera_name in cameras_dict:
        camera = libfli.get_camera(cameras_dict[camera_name]['serial'])
        assert camera is not None
        assert camera.serial == cameras_dict[camera_name]['serial']
        assert camera.model == cameras_dict[camera_name]['model']


def test_bad_camera(libfli):

    with pytest.raises(flicamera.lib.FLIError):
        flicamera.lib.LibFLIDevice('bad_name', libfli.libc)


def test_get_camera_bad_serial(libfli):

    assert libfli.get_camera('BADSERIAL') is None


def test_exposure_time_left(cameras):

    assert len(cameras) > 0
    assert all(cameras)

    camera = cameras[0]

    camera.set_exposure_time(10)
    camera.start_exposure()

    exp_time_left_1 = camera.get_exposure_time_left()
    time.sleep(0.1)
    exp_time_left_2 = camera.get_exposure_time_left()

    assert exp_time_left_1 > 0
    assert exp_time_left_1 > exp_time_left_2


def test_read_temperature(cameras):

    camera = cameras[0]  # FLIDevice object
    device = camera.libc.devices[0]  # MockFLIDevice object

    assert camera.temperature['CCD'] == device.state['temperature']['CCD']
    assert camera.temperature['base'] == device.state['temperature']['base']


def test_set_temperature(cameras):

    camera = cameras[0]

    temp_initial = camera.temperature['CCD']

    camera.set_temperature(-10.)

    assert camera.temperature['CCD'] != temp_initial
    assert camera.temperature['CCD'] == -10


def test_get_visible_area(cameras):

    camera = cameras[0]
    device = camera.libc.devices[0]

    (ul_x, ul_y, lr_x, lr_y) = camera.get_visible_area()

    assert ul_x == device.state['ul_x']
    assert ul_y == device.state['ul_y']
    assert lr_x == device.state['lr_x']
    assert lr_y == device.state['lr_y']


def test_read_frame(cameras):

    camera = cameras[0]

    camera.set_exposure_time(0.1)
    camera.start_exposure()

    time.sleep(0.2)

    assert camera.get_exposure_time_left() == 0

    image = camera.read_frame()

    assert image.mean() > 400.

    (ul_x, ul_y, lr_x, lr_y) = camera.get_visible_area()

    assert image.shape == (lr_y - ul_y, lr_x - ul_x)
