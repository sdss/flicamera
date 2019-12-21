#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pathlib
import warnings

import pytest
import ruamel.yaml

from flicamera.lib import FLIDevice, LibFLI

from .helpers import MockFLIDevice, MockLibFLI


TEST_DATA = pathlib.Path(__file__).parent / 'data/test_data.yaml'


@pytest.fixture(scope='session')
def config():
    """Gets the test configuration."""

    YAML = ruamel.yaml.YAML()

    yield YAML.load(open(TEST_DATA))


@pytest.fixture
def mock_libfli(mocker):
    """Mocks the FLI library."""

    yield mocker.patch('ctypes.cdll.LoadLibrary', MockLibFLI)


@pytest.fixture
def libfli(mock_libfli, config):
    """Yields a LibFLI object with a mocked C libfli library."""

    warnings.filterwarnings('ignore', '.+was compiled without a copy of libfli.+')

    libfli = LibFLI()

    for camera in config['cameras']:
        libfli.lib.devices.append(MockFLIDevice(camera, **config['cameras'][camera]))

    yield libfli

    FLIDevice._instances = {}


@pytest.fixture
def cameras(libfli):
    """Returns the connected cameras."""

    cameras = []

    for device in libfli.lib.devices:
        serial = device.state['serial']
        cameras.append(libfli.get_camera(serial))

    yield cameras
