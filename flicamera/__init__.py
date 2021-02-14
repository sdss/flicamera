# encoding: utf-8
# isort:skip

import os

from sdsstools import get_config, get_package_version


NAME = "sdss-flicamera"

__version__ = get_package_version(__file__, "sdss-flicamera") or "dev"
config = get_config(
    "flicamera",
    config_file=os.path.join(os.path.dirname(__file__), "etc/flicamera.yaml"),
)

OBSERVATORY = os.environ.get("OBSERVATORY", "UNKNOWN")

from .camera import *
from .lib import LibFLI
