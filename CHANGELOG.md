# Changelog

## 0.7.2 - November 2, 2025

### 🔧 Fixed

* Update the `RECORD` file in wheels to reflect the deleted `cextern` files.


## 0.7.1 - November 1, 2025

### 🔧 Fixed

* Update `LDFLAGS` and `CFLAGS` to build wheels on macOS with Homebrew-installed libraries in the release workflow.


## 0.7.0 - November 1, 2025

### 🏷️ Changed

* Updated active S/N of cameras at LCO after replacement of GFA1 in October 2025.

### ⚙️ Engineering

* Migrate from `distutils` to `setuptools` to build the C extension.
* Use `uv` to manage Python dependencies.
* Lint and format code with `ruff`.


## 0.6.0, December 24, 2022

### ✨ Improved

* Allow to set an image area and trim region in the image parameters.
* Use custom image areas for the FVC at APO and LCO.
* Ensure that camera is closed and the handle released.
* Output when a camera connects/disconnects to the actor users.
* Only run timed status when cameras are connected, to avoid unnecessary warnings.
* Ensure `libfli` is available when then actor starts.

### ⚙️ Engineering

* Do not update `latest` Docker image for tagged versions.
* Update release workflow to build wheels for multiple architectures and versions.


## 0.5.0, September 11, 2022

### 🚀 New

* Added GFAs for LCO.
* Updated the APO cameras after GFA-1 and GFA-6 were replaced.
* Complete LCO header cards.

### ✨ Improved

* Allow to skip finding calibration files to save time. In this case `BIASFILE=""`.

### 🔧 Fixed

* Forced `sdsstools>=0.5.2` to fix the calculation of SJD.
* Avoid creating multiple `BIASFILE` header entries.


## 0.4.0 - June 5, 2022

### 🚀 New

* Added header keyword `BIASFILE` with the most recently taken bias image (on the same SJD).
* Added header keyword `SJD` with the SDSS custom Julian Day.

### 🏷️ Changed

* Output image directory now uses SJD (SDSS JD) from `sdsstools.time.get_sjd()` instead of the usual MJD.


## 0.3.0 - June 4, 2022

### ✨ Improved

* Skip disconnect if no cameras are connected.
* Use RICE_1 compression for the FVC.
* Add `Dockerfile_test` to create docker image using local versions of `basecam` and `flicamera`.

### 🔧 Fixed

* Do not fail if exposure time is 0.0.


## 0.2.2 - January 7, 2022

### ✨ Improved

* Avoid duplicated `integrating` messages.
* Better handling of some exceptions when camera disconnects.
* Improve FPS card descriptions.
* Improve connection to Tron.


## 0.2.1 - Decemeber 14, 2021

### ✨ Improved

* Used in conjunction with `basecam >=0.5.3` fixed the issue with compressed extensions not being read by some software.
* Added FPS cards to headers.
* Improvements to `Dockerfile`.


## 0.2.0 - August 2, 2021

### 🚀 New

* Add mostly complete header datamodel.
* Update configuration file with real S/N for all GFA and FVC. Set the correct image names and directory names.
* Add option to simulate cameras and exposures.
* Set temperature setpoint to -10C for FVC when camera is connected.

### ✨ Improved

* Use `furo` and `myst-parser` for documentation.
* Set umask to `002` in the Dockerfile so that new images get `rw` permissions when created on an NFS mount.

### 🧹 Clean

* Format with `black` and add types to most of the codebase.


## 0.1.2 - December 7, 2020

### 🔧 Fixed

* [#5](https://github.com/sdss/flicamera/issues/5) Fixed compilation of `libfli`. It was failing due to an issue with the libraries to be linked when outside RTD or GH environment.


## 0.1.1 - November 8, 2020

### 🚀 New

* [#3](https://github.com/sdss/flicamera/issues/3) Include `Dockerfile` to create an image that can run `flicamera`.

### ✨ Improved

* Simplified loading of the `libfli` library. Now it forces to use the inplace object.
* Completed documentation.


## 0.1.0 - August 2, 2020

### 🚀 New

* Initial version. Complete wrapping of the `libfli` library and `basecam` implementation, with tests. Placeholder but functional actor. CLI allows to start the actor, retrieve status, and take basic exposures.
