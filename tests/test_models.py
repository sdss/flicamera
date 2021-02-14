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
from flicamera.model import APOCards, APOTCCCards, LampCards, flicamera_model


pytestmark = [pytest.mark.asyncio]


@pytest.fixture(autouse=True)
async def set_obervatory(camera_system):
    camera_system.cameras[0].observatory = "APO"
    flicamera_model[0].header_model += [APOTCCCards(), LampCards(), APOCards()]
    yield


@pytest.fixture
def actor():
    class Tron:
        models = {
            "tcc": {"objSys": TronKey("objSys", ["ICRS"])},
            "mcp": {
                "ffsStatus": TronKey("ffsStatus", ["01", "10", "01", "BAD"]),
                "ffLamp": TronKey("ffLamp", [True, False, "BAD"]),
            },
        }

    class Actor:
        tron = Tron()

    yield Actor()


async def test_tcc_model(camera_system):

    camera = camera_system.cameras[0]
    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "UNKNOWN"


async def test_tcc_model_objsys_mount(camera_system, actor):

    camera = camera_system.cameras[0]

    actor.tron.models["tcc"]["objSys"].value = ["Mount"]

    FLICamera.fits_model.context.update({"__actor__": actor})
    camera.fits_model.context.update({"__actor__": actor})

    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "Mount"
    assert header["RA"] == "NaN"


async def test_tcc_model_objsys_icrs(camera_system, actor):

    camera = camera_system.cameras[0]

    actor.tron.models["tcc"]["objSys"].value = ["ICRS"]
    actor.tron.models["tcc"]["objNetPos"] = TronKey("objNetPos", [(121.0, 0.0, 1.0)])

    FLICamera.fits_model.context.update({"__actor__": actor})
    camera.fits_model.context.update({"__actor__": actor})

    exposure = await camera.expose(0.1)

    header = exposure.to_hdu()[1].header
    assert "OBJSYS" in header
    assert header["OBJSYS"] == "ICRS"
    assert header["RA"] == 121.0
