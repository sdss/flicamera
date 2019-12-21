#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-20
# @Filename: helpers.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import ctypes
import unittest.mock


class MockLibFLI(ctypes.CDLL):
    """Mocks the CDLL object with the FLI dynamic library."""

    def __init__(self, dlpath):

        self.dlpath = dlpath
        self.reset()

    def reset(self):
        """Sets the initial values of the mocked device."""

        self.temperature = {'CCD': 25, 'base': 20}

    def __getattr__(self, name):

        if name in dir(self):
            return super(MockLibFLI, self).__getattr__(name)

        return unittest.mock.MagicMock()

    def test_method(self):
        pass
