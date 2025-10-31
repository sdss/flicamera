#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-17
# @Filename: build.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

# Extension build system using poetry, see
# https://github.com/python-poetry/poetry/issues/11.

import glob
import os
import shutil
import sys
import tempfile
import zipfile

from setuptools import Extension, setup
from setuptools.command.bdist_wheel import bdist_wheel


LIBFLI_PATH = "flicamera/cextern/libfli-1.999.1-180223"

RTD = os.environ.get("READTHEDOCS", False)


def get_directories():
    dirs = [LIBFLI_PATH]

    if sys.platform in ["linux", "darwin", "unix"]:
        dirs.append(os.path.join(LIBFLI_PATH, "unix"))
        if not RTD:  # Add the libusb directory except when in RTD.
            dirs.append(os.path.join(LIBFLI_PATH, "unix", "libusb"))

    return dirs


def get_sources():
    dirs = get_directories()

    sources = []
    for dir_ in dirs:
        sources += glob.glob(dir_ + "/*.c")

    return sources


extra_compile_args = ["-O3", "-fPIC", "-g"]
extra_link_args = []

# Do not use libusb on RTD because it makes the build fail.
# This still creates a usable library and we are mocking the device anyway.
if RTD:
    libraries = ["m"]
else:
    libraries = ["m", "usb-1.0"]


class CustomWheelCommand(bdist_wheel):
    """Custom wheel command to remove cextern files from the wheel."""

    def run(self):
        super().run()  # Create wheel normally

        # Now we read the wheel file and re-create it without the cextern files.
        dist_dir = self.dist_dir
        if dist_dir is None:
            return

        for fname in os.listdir(dist_dir):
            if not fname.endswith(".whl"):
                continue
            wheel_path = os.path.join(dist_dir, fname)
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".whl")
            os.close(tmp_fd)
            try:
                with (
                    zipfile.ZipFile(wheel_path, "r") as zin,
                    zipfile.ZipFile(
                        tmp_path,
                        "w",
                        compression=zipfile.ZIP_DEFLATED,
                    ) as zout,
                ):
                    prefix = "flicamera/cextern/"
                    for item in zin.infolist():
                        if item.filename.startswith(prefix):
                            # skip cextern files
                            continue
                        data = zin.read(item.filename)
                        zout.writestr(item, data)
                shutil.move(tmp_path, wheel_path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


ext_modules = [
    Extension(
        "flicamera.libfli",
        sources=get_sources(),
        include_dirs=get_directories(),
        libraries=libraries,
        define_macros=[("__LIBUSB__", "1")],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c",
        optional=False,
    ),
]


setup(ext_modules=ext_modules, cmdclass={"bdist_wheel": CustomWheelCommand})
