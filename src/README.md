libFLI
======

The current version of the libFLI library (1.104) does not compile correctly with recent versions of MacOS. It also produces a static library that cannot be easily wrapped with Python. The code copied here contains two modifications to the original source:

- The Makefile has been modified to work with recent versions of MacOS and produces a shared library ``libfli.so``.

- ``unix/libfli-sys.h`` has been modified to prevent a duplicate symbol definition.

- ``libfli.c`` has been modified to include the MacOS definition for ``usb_bulktransfer`` (see [here](https://github.com/cversek/python-FLI/issues/5#issuecomment-129927593)).

These changes have been tested with MacOS 10.15+ and Unix. **gfa does not require to manually compile the library**. In normal situations, building gfa will automatically generate a shared library from these modified sources.

Documentation for the SDK is available [here](http://www.flicamera.com/downloads/FLI_SDK_Documentation.pdf).
