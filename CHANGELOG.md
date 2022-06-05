# Changelog

## Next version

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
