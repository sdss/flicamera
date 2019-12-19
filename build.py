#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-12-17
# @Filename: build.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

# Extension build system using poetry, see https://github.com/python-poetry/poetry/issues/11.

import glob
import os
import sys

from setuptools import Extension


LIBFLI_PATH = os.path.join(os.path.dirname(__file__), 'cextern/libfli-1.999.1-180223')


def get_directories():

    dirs = [LIBFLI_PATH]

    if sys.platform in ['linux', 'darwin', 'unix']:
        dirs.append(os.path.join(LIBFLI_PATH, 'unix'))
        dirs.append(os.path.join(LIBFLI_PATH, 'unix', 'libusb'))

    return dirs


def get_sources():

    dirs = get_directories()

    sources = []
    for dir_ in dirs:
        sources += glob.glob(dir_ + '/*.c')

    return sources


extra_compile_args = ['-D__LIBUSB__', '-Wall', '-O3', '-fPIC', '-g']
extra_link_args = ['-lm', '-nostartfiles']

ext_modules = [
    Extension(
        'flicamera.libfli',
        sources=get_sources(),
        include_dirs=get_directories(),
        libraries=['usb-1.0'],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language='c'
    )
]


def build(setup_kwargs):
    """To build the extensions with poetry."""

    setup_kwargs.update({
        'ext_modules': ext_modules,
    })
