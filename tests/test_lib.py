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
