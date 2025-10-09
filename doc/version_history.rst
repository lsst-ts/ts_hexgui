.. py:currentmodule:: lsst.ts.hexgui

.. _lsst.ts.hexgui-version_history:

##################
Version History
##################

.. _lsst.ts.hexgui-0.5.2:

-------------
0.5.2
-------------

* Update the **ts-conda-build**.

.. _lsst.ts.hexgui-0.5.1:

-------------
0.5.1
-------------

* Fix the comment in **Config** of ``structs.py``.

.. _lsst.ts.hexgui-0.5.0:

-------------
0.5.0
-------------

* Update the ``structs.py`` to reflect the interface change in **ts_hexapod_controller** v1.8.0.

.. _lsst.ts.hexgui-0.4.5:

-------------
0.4.5
-------------

* Simplify the ``setup.py``.

.. _lsst.ts.hexgui-0.4.4:

-------------
0.4.4
-------------

* Add the **QT_QPA_PLATFORM** to ``meta.yaml`` to fix the test section of conda recipe.

.. _lsst.ts.hexgui-0.4.3:

-------------
0.4.3
-------------

* Use the configuration file of version 5.

.. _lsst.ts.hexgui-0.4.2:

-------------
0.4.2
-------------

* Improve the ``setup.py`` to support the version of Python 3.11 and 3.12.

.. _lsst.ts.hexgui-0.4.1:

-------------
0.4.1
-------------

* Remove the **ts_idl**.

.. _lsst.ts.hexgui-0.4.0:

-------------
0.4.0
-------------

* Update the **control_panel.py** to set the current configured velocity and acceleration.
* Tune the format of **tab_config.py**.
* Fix the unit in **model.py**.
* Add the user guide and error handling documents.
* Support the simulation mode.
* Fix the **MAX_ACTUATOR_RANGE_MIC** in **constants.py**.

.. _lsst.ts.hexgui-0.3.0:

-------------
0.3.0
-------------

* Depend on the **ts_hexrotcomm**.
* Copy the **structs.py** from the **ts_mthexapod**.
* Add the limits to **contants.py**.
* Update the enum value to be consistent with the **ts_hexapod_controller**.
* Remove the **config.py**.
* Fix the input pin in **TabDriveStatus**.
* Use the mirco degree in **TabPosition**.
* Support the TCP/IP communication with the controller.
* Update the range of parameters in **ControlPanel**.
* Update the **MainWindow** to connect/disconnect the controller.
* Extract the **TabConfig** from **TabTelemetry**.
* Update the **TabTelemetry** to show the current data.
* Remove the log button in **ControlPanel**.

.. _lsst.ts.hexgui-0.2.0:

-------------
0.2.0
-------------

* Read the configuration file in **ts_config_mttcs**.
* Add the **signals.py**, **config.py**, and **status.py**.

.. _lsst.ts.hexgui-0.1.0:

-------------
0.1.0
-------------

* Initial framework.
