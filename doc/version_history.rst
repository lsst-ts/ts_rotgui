.. py:currentmodule:: lsst.ts.rotgui

.. _lsst.ts.rotgui-version_history:

##################
Version History
##################

.. _lsst.ts.rotgui-0.4.1:

-------------
0.4.1
-------------

* Add the user guide and error handling documents.

.. _lsst.ts.rotgui-0.4.0:

-------------
0.4.0
-------------

* Depend on the **ts_hexrotcomm**.
* Copy the **structs.py** from the **ts_mtrotator**.
* Add the ``MAX_ACCELERATION`` and ``MAX_JERK`` to **contants.py**.
* Update the enum value to be consistent with the **ts_rotator_controller**.
* Remove the **config.py**.
* Fix the input pin in **TabDriveStatus**.
* Support the TCP/IP communication with the controller.
* Update the **MainWindow** to connect/disconnect the controller.
* Extract the **TabConfig** from **TabTelemetry**.
* Update the **TabTelemetry** to show the current data.
* Remove the log button in **ControlPanel**.
* Support the simulation mode.

.. _lsst.ts.rotgui-0.3.2:

-------------
0.3.2
-------------

* Remove the **ts_idl**.

.. _lsst.ts.rotgui-0.3.1:

-------------
0.3.1
-------------

* Fix the **Jenkinsfile.conda**.
* Use the **NUM_STRUT** in the **Model** class.
* Fix the format.
* Update the **class_rotgui.mmd**.

.. _lsst.ts.rotgui-0.3.0:

-------------
0.3.0
-------------

* Rename ``run_application()`` to ``run_gui()``.
* Read the configuration file in **ts_config_mttcs**.
* Add the **signals.py**, **config.py**, and **status.py**.

.. _lsst.ts.rotgui-0.2.0:

-------------
0.2.0
-------------

* Implement the telemetry and power widgets.
* Add the new commands to control panel.
* Move the functions from the drive status and control panel widgets to **ts_guitool**.

.. _lsst.ts.rotgui-0.1.0:

-------------
0.1.0
-------------

* Initial framework.
