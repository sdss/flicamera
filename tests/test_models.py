#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-02-13
# @Filename: test_models.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import pytest

from clu.legacy import TronKey

from flicamera.camera import FLICamera


pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def actor():
    class Tron:
        models = {"tcc": {"objSys": TronKey("objSys", ["ICRS"])}}

    class Actor:
        tron = Tron()

    yield Actor()


async def test_tcc_model(camera_system):

    camera = camera_system.cameras[0]
    camera.observatory = "APO"

    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "UNKNOWN"


async def test_tcc_model_objsys_mount(camera_system, actor):

    camera = camera_system.cameras[0]
    camera.observatory = "APO"

    actor.tron.models["tcc"]["objSys"].value = ["Mount"]

    FLICamera.fits_model.context.update({"__actor__": actor})
    camera.fits_model.context.update({"__actor__": actor})

    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "Mount"
    assert header["RA"] == "NaN"


@pytest.mark.xfail
async def test_tcc_model_objsys_icrs(camera_system, actor):

    camera = camera_system.cameras[0]
    camera.observatory = "APO"

    actor.tron.models["tcc"]["objSys"].value = ["ICRS"]
    actor.tron.models["tcc"]["objNetPos"] = TronKey("objNetPos", [(121.0, 0.0, 1.0)])

    FLICamera.fits_model.context.update({"__actor__": actor})
    camera.fits_model.context.update({"__actor__": actor})

    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "ICRS"
    assert header["RA"] == 121.0
