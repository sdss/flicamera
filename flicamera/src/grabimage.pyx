#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-21
# @Filename: grabimage.pyx
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import numpy


ctypedef long LIBFLIAPI
ctypedef long flidev_t

cdef extern LIBFLIAPI FLIGrabRow(flidev_t dev, void *buff, size_t width)


def grab_image(flidev_t dev, size_t n_rows, size_t n_cols):
    """Fetches an image from the FLI library row by row."""

    arr = numpy.empty((n_rows, n_cols), dtype=numpy.uint16)

    # Just to be sure.
    if not arr.flags['C_CONTIGUOUS']:
        arr = numpy.ascontiguousarray(arr)

    cdef unsigned int [:, :] arr_view = arr
    cdef unsigned int ii

    for ii in range(n_rows):
        FLIGrabRow(dev, &arr_view[ii, 0], n_cols)

    return arr
