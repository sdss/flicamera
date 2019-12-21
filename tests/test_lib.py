#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: test_lib.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

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
