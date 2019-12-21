#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-18
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest
import warnings

from flicamera.lib import LibFLI

from .helpers import MockLibFLI


@pytest.fixture
def mock_libfli(mocker):
    """Mocks the FLI library."""

    yield mocker.patch('ctypes.cdll.LoadLibrary', MockLibFLI)


@pytest.fixture
def libfli(mock_libfli):

    warnings.filterwarnings('ignore', '.+was compiled without a copy of libfli.+')
    yield LibFLI()
