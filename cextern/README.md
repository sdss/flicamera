libFLI
======

The current version of the libFLI library ([1.104](http://www.flicamera.com/downloads/sdk/libfli-1.104.zip)) does not compile correctly with recent versions of MacOS, and seems to require modifications to the kernel in Linux to work with USB cameras. The 1.999.1 pre-release version seems to fix these problems and it's recommended. The standard Makefile also only produces a static library that cannot be easily wrapped with Python. The copied here has been modified so that the Makefile produces the shared a shared libary.

These changes have been tested with MacOS 10.15+ and Unix. **flicamera does not require you to manually compile the library**. In normal situations, building flicamera will automatically generate a shared library from these modified sources.

Note that in addition to these files, your system needs `libusb-1.0` and the associated header files installed in a system location. Depending on your system, you may also need to add a rule to allow access to the USB device. To do that, in Ubuntu:

- Create a new udev rules, file, for example `/etc/udev/rules.d/99-usb.rules`.
- Add the following line `SUBSYSTEM=="usb", ATTR{idVendor}=="0f18", GROUP="sudo", MODE="0666"`. This provides access to all users in the group sudo to the USBs of vendor `0f18` (Finger Lakes Instrumentation). You may need to change this to match your group.
- Run `sudo service udev restart` and `sudo udevadm control --reload-rules` and replug the camera.

Many of these details are taken from the [PANOPTES POCS](https://github.com/panoptes/POCS/wiki/Additional-Hardware-Drivers-Installation#finger-lake-instruments).

Documentation for the SDK is available [here](http://www.flicamera.com/downloads/FLI_SDK_Documentation.pdf) and [added to this repository](https://github.com/sdss/flicamera/blob/master/cextern/FLI_SDK_Documentation.pdf). Note that some functions in the SDK are not documented.

Some notes on the API:

- The `FLIGetDeviceStatus` function doesn't see to produce reasonable values, and in fact it is not used in most implementations. It may be camera dependant but ultimately it doesn't seem necessary.

- `FLIGetArrayArea` seems to returns the same value as `FLIGetVisibleArea` but without the offset. For example, if `FLIGetVisibleArea` returns `(64, 45, 8240, 6177)` then `FLIGetArrayArea` will return `(0, 0, 8304, 6220)`. Neither of them changes when `FLISetImageArea` is called or when the binning changes. No implementation actually uses it.

- It is unclear how the visible area relates the actual pixels on the CCD. For example, if the visible area is `(64, 45, 8240, 6177)`, is 64 the first pixel on the CCD or the 64th (or 63rd) and the pixels 1-63 are not read? This is important when calibrating the position of the CCD with respect to a fiducial.

- There are a number of functions in the API that are not documented (e.g., `FLISetTDI`, `FLIGetDeviceStatus`, etc.)

- Trying to set `FLISetBitDepth` to `FLI_MODE_16BIT` fails with error "Invalid argument".

- Some code has been adapted from [python-FLI](https://github.com/cversek/python-FLI).
