# flicamera

![Versions](https://img.shields.io/badge/python->3.10-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-flicamera/badge/?version=latest)](https://sdss-flicamera.readthedocs.io/en/latest/?badge=latest)
[![Tests Status](https://github.com/sdss/flicamera/workflows/Test/badge.svg)](https://github.com/sdss/flicamera/actions/workflows/test.yml)
[![Build](https://github.com/sdss/flicamera/actions/workflows/build.yml/badge.svg)](https://github.com/sdss/flicamera/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/sdss/flicamera/branch/main/graph/badge.svg?token=2kayI7e8UB)](https://codecov.io/gh/sdss/flicamera)

A library to control Finger Lakes Instrumentation cameras. It provides the SDSS `gfaCamera` and `fvcCamera` actors to control the Guide, Focus and Acquisition cameras and Field View Camera, respectively.

## Installation

In general you should be able to install ``flicamera`` by doing

```console
pip install sdss-flicamera
```

Although `flicamera` should handle all the compilation of the FLI libraries, you may still need to modify your system to give your user access to the FLI USB devices. See [here](https://github.com/sdss/flicamera/blob/master/cextern/README.md) for more details.

To build from source, use

```console
git clone git@github.com:sdss/flicamera
cd flicamera
pip install -e .
```
