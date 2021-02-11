# encoding: utf-8
# isort:skip

from sdsstools import get_package_version


NAME = "sdss-flicamera"

__version__ = get_package_version(__file__, "sdss-flicamera") or "dev"


from .camera import *
