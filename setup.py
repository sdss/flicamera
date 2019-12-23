# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flicamera', 'flicamera.utils']

package_data = \
{'': ['*'], 'flicamera': ['etc/*', 'src/*']}

install_requires = \
['numpy>=1.17.4,<2.0.0',
 'pygments>=2.2.0,<3.0.0',
 'ruamel.yaml>=0.15.61,<0.16.0',
 'sdss-basecam @ git+https://github.com/sdss/basecam.git@master']

extras_require = \
{'docs': ['Sphinx>=2.1,<3.0', 'semantic-version==2.8.0']}

setup_kwargs = {
    'name': 'sdss-flicamera',
    'version': '0.1.0a0',
    'description': 'A library to control Finger Lakes Instrumentation cameras.',
    'long_description': '# flicamera\n\n![Versions](https://img.shields.io/badge/python->3.7-blue)\n[![Documentation Status](https://readthedocs.org/projects/sdss-flicamera/badge/?version=latest)](https://sdss-flicamera.readthedocs.io/en/latest/?badge=latest)\n[![Travis (.org)](https://img.shields.io/travis/sdss/flicamera)](https://travis-ci.org/sdss/flicamera)\n[![codecov](https://codecov.io/gh/sdss/flicamera/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/flicamera)\n\nA library to control Finger Lakes Instrumentation cameras. It provides the SDSS ``gfaCamera`` and ``fvcCamera`` actors to control the Guide, Focus and Acquisition cameras and Field View Camera, respectively.\n\n## Installation\n\nIn general you should be able to install ``flicamera`` by doing\n\n```console\npip install sdss-flicamera\n```\n\nAlthough ``flicamera`` should handle all the compilation of the FLI libraries, you may still need to modify your system to give your user access to the FLI USB devices. See [here](https://github.com/sdss/flicamera/blob/master/cextern/README.md) for more details.\n\n``flicamera`` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. Unfortunately, poetry provides a ``setup.py``-less build system that prevents ``python setup.py install`` or ``pip install .`` from working (the latter due to the fact that ``flicamera`` requires compilation of extensions during the build process, see [here](https://github.com/python-poetry/poetry/issues/1516) for details). As a workaround, we provide a script, ``create_setup.py`` that generates a temporary ``setup.py`` file with all the metadata from the ``pyproject.toml`` file. To build ``flicamera`` manually do\n\n```console\npython create_setup.py\npython setup.py build\npython setup.py install\n```\n\nor\n\n```console\npython create_setup.py\npip install .\n```\n',
    'author': 'José Sánchez-Gallego',
    'author_email': 'gallegoj@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdss/flicamera',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)

# This setup.py was autogenerated using poetry.
