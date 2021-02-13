#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-21
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import Any, Optional

from basecam.actor import CameraActor
from clu.command import TimedCommand
from clu.legacy import TronConnection

from flicamera.camera import FLICamera, FLICameraSystem


class FLIActor(CameraActor):
    def __init__(
        self,
        camera_system: FLICameraSystem,
        *args,
        data_dir: Optional[str] = None,
        image_name: Optional[str] = None,
        tron: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        self.camera_system = camera_system
        super().__init__(camera_system, *args, **kwargs)

        # The default image namer writes to ./ For production we want to write to /data.
        _data_dir: str = data_dir or "./"
        _image_name: str = image_name or "{camera.name}-{num:04d}.fits"

        FLICamera.image_namer.dirname = _data_dir
        FLICamera.image_namer.basename = _image_name

        # Also need to update the context of the fits model.
        FLICamera.fits_model.context.update({"__actor__": self})

        # If the actor is started from __main__.py, the camera_system is already
        # running and cameras may be attached. The changes above won't affect the
        # instance attributes of those cameras. We need to change the image namer
        # and fits_model of any already connected camera.
        for camera in self.camera_system.cameras:
            camera.image_namer.basename = _image_name
            camera.image_namer.dirname = _data_dir
            camera.image_namer.camera = camera
            camera.fits_model.context.update({"__actor__": self})

        if tron:
            self.tron = TronConnection(tron["host"], tron["port"])
        else:
            self.tron = None

        self.timed_commands.append(TimedCommand("status", delay=60))

    async def start(self):
        """Reconnects the camera system if no cameras are connected."""

        await super().start()
        if self.tron:
            await self.tron.start()

        if self.camera_system.running or len(self.camera_system.cameras) > 0:
            return self

        self.camera_system.setup()

        return self
