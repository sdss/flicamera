#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-21
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import warnings

from typing import Any, Dict, Optional

from basecam.actor import CameraActor
from basecam.events import CameraEvent, CameraSystemEvent
from clu import Command
from clu.legacy import TronConnection

from flicamera import OBSERVATORY
from flicamera.camera import FLICamera, FLICameraSystem
from flicamera.lib import FLIWarning


class FLIActor(CameraActor):
    """Flicamera actor."""

    def __init__(
        self,
        camera_system: FLICameraSystem,
        *args,
        data_dir: Optional[str] = None,
        image_name: Optional[str] = None,
        tron: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):

        self.observatory = OBSERVATORY

        self.camera_system = camera_system
        super().__init__(camera_system, *args, validate=False, **kwargs)

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

        self.listener.register_callback(self.event_listener)

        if tron:
            try:
                import actorkeys  # type: ignore  # noqa

                tron_host = tron["host"]
                tron_port = tron["port"]

                self.log.debug(f"Connecting to Tron on ({tron_host}, {tron_port})")

                observatory_models = tron.get("observatory_models", {})
                models = tron["models"] + observatory_models.get(self.observatory, [])

                self.tron = TronConnection(
                    f"flicamera.{self.name}",
                    tron["host"],
                    tron["port"],
                    models=models,
                    log=self.log,
                )
            except ImportError:
                warnings.warn(
                    "Failed connecting to Tron. actorkeys is not present.",
                    FLIWarning,
                )
                self.tron = None

        else:
            self.tron = None

        asyncio.create_task(self._output_status())

    async def start(self):
        """Reconnects the camera system if no cameras are connected."""

        await super().start()

        if self.tron:
            try:
                await self.tron.start()
                self.log.debug("Connection to Tron established.")
            except OSError:
                warnings.warn(
                    "Failed connecting to Tron. This may affect some functionality.",
                    FLIWarning,
                )
                self.tron = None

        if self.camera_system.running or len(self.camera_system.cameras) > 0:
            return self

        self.camera_system.setup()

        return self

    async def _output_status(self):
        """Outputs the camera status."""

        while True:
            # Only call status if there are cameras connected, to avoid raising
            # unnecessary warnings.
            if len(self.camera_system.cameras) > 0:
                await Command(
                    "status",
                    actor=self,
                    commander_id=f".{self.name}",
                ).parse()

            await asyncio.sleep(120)

    def event_listener(self, event: CameraSystemEvent | CameraEvent, payload):
        """Listens to events from the camera system."""

        if event == CameraEvent.CAMERA_CONNECTED:
            name = payload["name"]
            self.write("i", text=f"Camera connected: {name}")
        elif event == CameraEvent.CAMERA_DISCONNECTED:
            name = payload["name"]
            self.write("i", text=f"Camera disconnected: {name}")
