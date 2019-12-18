# gfa

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/gfa/badge/?version=latest)](https://sdss-gfa.readthedocs.io/en/latest/?badge=latest)
[![Travis (.org)](https://img.shields.io/travis/sdss/gfa)](https://travis-ci.org/sdss/gfa)
[![codecov](https://codecov.io/gh/sdss/gfa/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/gfa)

A library and actor to control the Guide, Focus, and Acquisition cameras.

## Installation

In general you should be able to install ``gfa`` by doing

```console
pip install sdss-gfa
```

``gfa`` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. Unfortunately, poetry provides a ``setup.py``-less build system that prevents ``python setup.py install`` or ``pip install .`` from working (the latter due to the fact that ``gfa`` requires compilation of extensions during the build process, see [here](https://github.com/python-poetry/poetry/issues/1516) for details). As a workaround, we provide a script, ``create_setup.py`` that generates a temporary ``setup.py`` file with all the metadata from the ``pyproject.toml`` file. To build ``gfa`` manually do

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
