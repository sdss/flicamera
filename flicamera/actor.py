#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-21
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import Optional

from basecam.actor import CameraActor
from clu.command import TimedCommand


class FLIActor(CameraActor):
    def __init__(
        self,
        *args,
        data_dir: Optional[str] = None,
        image_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # The default image namer writes to ./ For production we want to write to /data.
        _data_dir: str = data_dir or "./"
        _image_name: str = image_name or "{camera.name}-{num:04d}.fits"

        self.camera_system.camera_class.image_namer.dirname = _data_dir
        self.camera_system.camera_class.image_namer.basename = _image_name

        # We need to change the image namer of any already connected camera.
        for camera in self.camera_system.cameras:
            camera.image_namer.basename = _image_name
            camera.image_namer.dirname = _data_dir
            camera.image_namer.camera = camera

        self.timed_commands.append(TimedCommand("status", delay=60))
