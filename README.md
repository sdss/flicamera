# flicamera

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-flicamera/badge/?version=latest)](https://sdss-flicamera.readthedocs.io/en/latest/?badge=latest)
[![Travis (.org)](https://img.shields.io/travis/sdss/flicamera)](https://travis-ci.org/sdss/flicamera)
[![codecov](https://codecov.io/gh/sdss/flicamera/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/flicamera)

A library to control Finger Lakes Instrumentation cameras. It provides the SDSS ``gfaCamera`` and ``fvcCamera`` actors to control the Guide, Focus and Acquisition cameras and Field View Camera, respectively.

## Installation

In general you should be able to install ``flicamera`` by doing

```console
pip install sdss-flicamera
```

Although ``flicamera`` should handle all the compilation of the FLI libraries, you may still need to modify your system to give your user access to the FLI USB devices. See [here](https://github.com/sdss/flicamera/blob/master/cextern/README.md) for more details.

``flicamera`` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. Unfortunately, poetry provides a ``setup.py``-less build system that prevents ``python setup.py install`` or ``pip install .`` from working (the latter due to the fact that ``flicamera`` requires compilation of extensions during the build process, see [here](https://github.com/python-poetry/poetry/issues/1516) for details). As a workaround, we provide a script, ``create_setup.py`` that generates a temporary ``setup.py`` file with all the metadata from the ``pyproject.toml`` file. To build ``flicamera`` manually do

```console
python create_setup.py
python setup.py build
python setup.py install
```

or

```console
python create_setup.py
pip install .
```
