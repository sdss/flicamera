=========
Changelog
=========

* :release:`0.1.2 <2020-12-07>`
* :bug:`5` Fixed compilation of ``libfli``. It was failing due to an issue with the libraries to be linked when outside RTD or GH environment.

* :release:`0.1.1 <2020-11-08>`
* :feature:`3` Include ``Dockerfile`` to create an image that can run ``flicamera``.
* :support:`-` Simplified loading of the ``libfli`` library. Now it forces to use the inplace object.
* Completed documentation.

* :release:`0.1.0 <2020-08-02>`
* Initial version. Complete wrapping of the ``libfli`` library and ``basecam`` implementation, with tests. Placeholder but functional actor. CLI allows to start the actor, retrieve status, and take basic exposures.
