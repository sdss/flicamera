# Changelog

## Next version

### 🚀 New

* Add mostly complete header datamodel.
* Update configuration file with real S/N for all GFA and FVC. Set the correct image names and directory names.
* Add option to simulate cameras and exposures.

### ✨ Improved

* Use `furo` and `myst-parser` for documentation.

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