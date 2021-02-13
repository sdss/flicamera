# flicamera

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/sdss-flicamera/badge/?version=latest)](https://sdss-flicamera.readthedocs.io/en/latest/?badge=latest)
[![Tests Status](https://github.com/sdss/flicamera/workflows/Test/badge.svg)](https://github.com/sdss/flicamera/actions)
[![Build Status](https://github.com/sdss/flicamera/workflows/Build/badge.svg)](https://github.com/sdss/flicamera/actions)
[![codecov](https://codecov.io/gh/sdss/flicamera/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/flicamera)

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
pip install .[docs]
```

## Development

`flicamera` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. To work with an editable install it's recommended that you setup `poetry` and install `flicamera` in a virtual environment by doing

```console
poetry install
```

Pip does not support editable installs with PEP-517 yet. That means that running `pip install -e .` will fail because `poetry` doesn't use a `setup.py` file. As a workaround, you can use the `create_setup.py` file to generate a temporary `setup.py` file. To install `flicamera` in editable mode without `poetry`, do

```console
pip install --pre poetry
python create_setup.py
pip install -e .
```
