#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-02-12
# @Filename: model.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from basecam.models import Card, CardGroup, Extension, FITSModel, HeaderModel


__all__ = ["flicamera_model"]


window_group = CardGroup(
    [
        Card(
            "BEGX",
            "{__camera__._device.area[0]}",
            "Window start pixel in X",
            default=-999,
        ),
        Card(
            "BEGY",
            "{__camera__._device.area[1]}",
            "Window start pixel in Y",
            default=-999,
        ),
        Card(
            "ENDX",
            "{__camera__._device.area[2]}",
            "Window end pixel in X",
            default=-999,
        ),
        Card(
            "EDNY",
            "{__camera__._device.area[3]}",
            "Window end pixel in Y",
            default=-999,
        ),
        Card(
            "BINX",
            "{__camera__._device.hbin}",
            "Binning in X",
            default=-999,
        ),
        Card(
            "BINY",
            "{__camera__._device.vbin}",
            "Binning in Y",
            default=-999,
        ),
    ],
    name="window",
    use_group_title=False,
)


apo_raw_header_model = HeaderModel(
    [
        "VCAM",
        "IMAGETYP",
        "EXPTIME",
        Card(
            "TIMESYS",
            "TAI",
            "Time reference system",
        ),
        Card(
            "DATE-OBS",
            "{__exposure__.obstime.tai}",
            "Time of the start of the exposure [TAI]",
        ),
        Card(
            "CCDTEMP",
            "{__camera__.status[temperature_ccd]}",
            "Degrees C",
            default=-999.0,
        ),
        "STACK",
        "STACKFUN",
        "EXPTIMEN",
        window_group,
        Card(
            "GAIN",
            "{__camera__.gain}",
            "The CCD gain [e-/ADUs]",
            default=-999.0,
            type=float,
        ),
        Card(
            "READNOIS",
            "{__camera__.read_noise}",
            "The CCD read noise [ADUs]",
            default=-999.0,
            type=float,
        ),
        Card(
            "PIXELSC",
            "{__camera__.pixel_scale}",
            "Scale of unbinned pixel on sky [arcsec/pix]",
            default=-999.0,
            type=float,
        ),
        Card(
            "OBSERVAT",
            "{__camera__.observatory}",
            "Observatory",
            default="",
        ),
    ]
)

flicamera_model = FITSModel(
    [
        Extension(
            data=None,
            header_model=apo_raw_header_model,
            name="raw",
            compressed="GZIP_2",
        )
    ]
)
