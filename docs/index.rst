
.. highlight:: console

flicamera's documentation
=========================

This is the Sphinx documentation for the SDSS Python product ``flicamera``. This documentation is for version |flicamera_version|.


Getting started
---------------

``flicamera`` is a wrapper around the `libfli <https://www.flicamera.com/downloads/FLI_SDK_Documentation.pdf>`__ library for `Finger Lakes Instrumentation <https://www.flicamera.com>`__ cameras. It is built on top of `basecam <https://sdss-basecam.readthedocs.io/en/latest/>`__.

To install ``flicamera`` do ::

  $ pip install sdss-flicamera

Then you can run the actor as ::

  $ flicamera start

More options and command, some of which allow to command the camera without executing the actor, can be consulted :ref:`here <cli>` or by running ``flicamera --help``.

``flicamera`` can also be :ref:`run as a Docker <docker>`.


Contents
--------

.. toctree::
  :maxdepth: 2

  Configuring a computer <nuc>
  docker
  api
  CLI <cli>
  changelog



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
