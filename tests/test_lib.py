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
    assert len(libfli.lib.devices) > 0


def test_list_cameras(libfli):

    assert len(libfli.list_cameras()) > 0


def test_get_camera(libfli, config):

    cameras_dict = config['cameras']

    for camera_name in cameras_dict:
        camera = libfli.get_camera(cameras_dict[camera_name]['serial'])
        assert camera is not None
        assert camera.serial == cameras_dict[camera_name]['serial']


def test_bad_camera(libfli):

    with pytest.raises(flicamera.lib.FLIError):
        flicamera.lib.FLIDevice('bad_name', libfli.lib)


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
