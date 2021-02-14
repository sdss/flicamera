#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-02-12
# @Filename: model.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import Any, List, Tuple, Union

from basecam.exposure import Exposure
from basecam.models import (
    Card,
    CardGroup,
    Extension,
    FITSModel,
    HeaderModel,
    MacroCard,
    WCSCards,
)
from clu.legacy.types.pvt import PVT

import flicamera


__all__ = ["flicamera_model"]


MacroCardReturnType = List[Union[Tuple[str, Any], Tuple[str, Any, str], Card]]


def pvt2pos(tup):
    pvt = PVT(*tup)
    return pvt.getPos()


# TODO: this should be moved to CLU.


class TronModelCards(MacroCard):
    model = None

    def get(self, key, idx=0, default="NaN", cnv=None):
        if not self.model:
            return default

        try:
            value = self.model[key].value[idx]
            if cnv:
                value = cnv(value)
            return value
        except BaseException:
            return default


class TCCCards(TronModelCards):
    """Return a list of Cards describing the TCC state."""

    name = "TCC Cards"

    def macro(self, exposure: Exposure, context: dict[str, Any] = {}):
        if not isinstance(exposure.camera, flicamera.camera.FLICamera):
            return ()

        if exposure.camera.observatory == "APO":
            return self._apo_macro(exposure, context=context)
        else:
            return ()

    def _apo_macro(
        self,
        exposure: Exposure,
        context: dict[str, Any] = {},
    ) -> MacroCardReturnType:

        cards: MacroCardReturnType = []

        if (
            "__actor__" not in context
            or not hasattr(context["__actor__"], "tron")
            or context["__actor__"].tron is None
        ):
            self.model = None
        else:
            self.model = context["__actor__"].tron.models["tcc"]

        objSysName = self.get("objSys", 0, default="UNKNOWN")
        cards.append(("OBJSYS", objSysName, "The TCC objSys"))

        # ObjSys
        if objSysName in ("None", "Mount", "Obs", "Phys", "Inst"):
            cards += [
                ("RA", "NaN", "Telescope is not tracking the sky"),
                ("DEC", "NaN", "Telescope is not tracking the sky"),
                ("RADEG", "NaN", "Telescope is not tracking the sky"),
                ("DECDEG", "NaN", "Telescope is not tracking the sky"),
                ("SPA", "NaN", "Telescope is not tracking the sky"),
            ]
        else:
            cards += [
                (
                    "RA",
                    self.get("objNetPos", 0, cnv=pvt2pos),
                    "RA of telescope boresight (deg)",
                ),
                (
                    "DEC",
                    self.get("objNetPos", 1, cnv=pvt2pos),
                    "Dec of telescope boresight (deg)",
                ),
                (
                    "RADEG",
                    self.get("objPos", 0, cnv=pvt2pos),
                    "RA of telescope pointing (deg)",
                ),
                (
                    "DECDEG",
                    self.get("objPos", 1, cnv=pvt2pos),
                    "Dec of telescope pointing (deg)",
                ),
                (
                    "SPA",
                    self.get("spiderInstAng", 0, cnv=pvt2pos),
                    "TCC SpiderInstAng",
                ),
            ]

        # Rotator
        cards += [
            (
                "ROTTYPE",
                self.get("rotType", 0, cnv=str, default="UNKNOWN"),
                "Rotator request type",
            ),
            (
                "ROTPOS",
                self.get("rotPos", 0, cnv=pvt2pos),
                "Rotator request type",
            ),
        ]

        # Offsets
        offsets = (
            ("boresight", "BOREOFF", "TCC Boresight offset, deg", False),
            ("objArcOff", "ARCOFF", "TCC ObjArcOff, deg", False),
            ("calibOff", "CALOFF", "TCC CalibOff, deg", True),
            ("guideOff", "GUIDOFF", "TCC GuideOff, deg", True),
        )
        for tcc_key, key, comment, do_rot in offsets:
            cards.append(
                (
                    key + "X",
                    self.get(tcc_key, 0, cnv=pvt2pos),
                    comment,
                )
            )
            cards.append(
                (
                    key + "Y",
                    self.get(tcc_key, 1, cnv=pvt2pos),
                    comment,
                )
            )
            if do_rot:
                cards.append(
                    (
                        key + "R",
                        self.get(tcc_key, 2, cnv=pvt2pos),
                        comment,
                    )
                )

        # Alt/Az
        cards += [
            (
                "AZ",
                self.get("axePos", 0, cnv=float),
                "Azimuth axis pos. (approx, deg)",
            ),
            (
                "ALT",
                self.get("axePos", 1, cnv=float),
                "Altitude axis pos. (approx, deg)",
            ),
            (
                "IPA",
                self.get("axePos", 2, cnv=float),
                "Rotator axis pos. (approx, deg)",
            ),
            (
                "FOCUS",
                self.get("secFocus", 0, cnv=float),
                "User-specified focus offset (um)",
            ),
        ]

        # M1/2 orientation
        orientNames = ("piston", "xtilt", "ytilt", "xtran", "ytran", "zrot")
        for mirror in (1, 2):
            for idx, name in enumerate(orientNames):
                cards.append(
                    (
                        ("M1" if mirror == 1 else "M2") + orientNames[idx],
                        self.get(
                            "primOrient" if mirror == 1 else "secOrient",
                            idx,
                            cnv=float,
                        ),
                        "TCC " + "PrimOrient" if mirror == 1 else "SecOrient",
                    )
                )

        cards.append(
            (
                "SCALE",
                self.get("scaleFac", 0, cnv=float),
                "User-specified scale factor",
            )
        )

        return cards


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
        WCSCards(),
        Card(
            "OBSERVAT",
            "{__camera__.observatory}",
            "Observatory",
            default="",
        ),
        TCCCards(),
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
