#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-08-01
# @Filename: test_camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pathlib

import numpy
import pytest

from flicamera import FLICameraSystem


def test_camera_system(camera_system):
    assert isinstance(camera_system, FLICameraSystem)
    assert len(camera_system.cameras) == 1


def test_list_cameras(camera_system):
    available_cameras = camera_system.list_available_cameras()

    assert len(available_cameras) == 1
    assert available_cameras[0] == "ML1234"


def test_get_status(camera_system):
    camera = camera_system.cameras[0]
    status = camera.get_status()

    assert isinstance(status, dict)


@pytest.mark.asyncio
async def test_temperature(camera_system):
    camera = camera_system.cameras[0]

    await camera.set_temperature(250)
    temperature = await camera.get_temperature()

    assert temperature == 250.0


@pytest.mark.asyncio
async def test_expose(camera_system):
    camera = camera_system.cameras[0]

    exposure = await camera.expose(0.1)

    assert numpy.mean(exposure.data)
    assert exposure.data.shape == (512, 512)


@pytest.mark.asyncio
async def test_binning(camera_system):
    camera = camera_system.cameras[0]

    await camera.set_binning(2, 2)
    assert await camera.get_binning() == (2, 2)

    exposure = await camera.expose(0.1)

    assert exposure.data.shape == (256, 256)


@pytest.mark.asyncio
async def test_area(camera_system):
    camera = camera_system.cameras[0]

    await camera.set_image_area(area=(0, 50, 0, 25))
    assert await camera.get_image_area() == (0, 50, 0, 25)

    exposure = await camera.expose(0.1)

    assert exposure.data.shape == (25, 50)


@pytest.mark.asyncio
async def test_expose_snapshot(camera_system, monkeypatch):
    camera = camera_system.cameras[0]

    monkeypatch.setitem(camera.camera_params, "write_snapshot", True)

    exposure = await camera.expose(0.1)

    filename = exposure.filename
    snap_path = pathlib.Path(".") / (filename.split(".")[0] + "-snap.fits")

    assert snap_path.exists()
    snap_path.unlink()
