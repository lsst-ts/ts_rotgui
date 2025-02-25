.. _Error_Handling:

################
Error Handling
################

For the normal troubling shooting, refer to the :ref:`lsst.ts.rotgui-error_troubleshooting`.
In some cases, you may need to debug the Copley drive directly.
See the :ref:`lsst.ts.rotgui-error_motor_drive_faults` for more information.

.. _lsst.ts.rotgui-error_troubleshooting:

Troubleshooting
===============

This section provides a guide to identify and troubleshoot potential problems that may occur with the rotators:

.. list-table:: Troubleshooting
   :widths: 30 70 70 120
   :header-rows: 1

   * - Fault
     - Errors Detected
     - Fault Condition
     - Recovery Procedure
   * - Safety Interlock
     - Safe Torque Off engaged on Copley XE2 drives due to safety interlock being activated (or not connected), rotator locking pin inserted, electrical cabinet power cycled, or internal wiring problem in cabinet.
     - Drives disabled, brakes applied, enter fault state, no ability to output torque.
     - Ensure safety interlock cable is connected (7403-C8100). Check that all safety interlock disable switches have been closed and reset switch has been cycled (always necessary on power-up). If both of the redundant disable signals were not activated and reclosed, safety relay will not reset and will display a fault. Check display lights on Pilz S4 and S7 relays and consult Pilz user manuals. Check internal cabinet wiring to safety relays. Once safety interlock fault cleared, transition out of fault state with clear-error trigger.
   * - Positive Limit Switch
     - Positive limit switch activated, wiring problem, or switch failure.
     - Drives disabled, brakes applied, enter fault state, motion not allowed in positive direction while switch remains tripped.
     - Check telemetry to determine if rotator position has exceeded +90 deg. If so, the switch is likely tripped. To move back off switch, send the mask-limit-switch command of the EUI and send clear-error command to move out of fault state. Use position-set command to move rotator off the switch. Investigate how software limits were exceeded. If the rotator position does not exceed +90 deg, check cabinet and cable wiring. Inspecting limit switch itself will require major disassembly.
   * - Negative Limit Switch
     - Negative limit switch activated, wiring problem, or switch failure.
     - Drives disabled, brakes applied, enter fault state, motion not allowed in negative direction while switch remains tripped.
     - Check telemetry to determine if rotator position has exceeded -90 deg. If so, the switch is likely tripped. To move back off switch, send the mask-Limit-switch command of the EUI and send clear-error command to move out of fault state. Use position-set command to move rotator off the switch. Investigate how software limits were exceeded. If the rotator position does not exceed -90 deg, check cabinet and cable wiring. Inspecting limit switch itself will require major disassembly.
   * - Following Error
     - Rotator position deviated from commanded position by more than threshold value indicating rotator is not moving at all or not tracking command as expected.
     - Drives disabled, brakes applied, and enter fault state.
     - If rotator did not appear to move at all, check to ensure that the motor power cables (7403-C6000) are connected to the correct motor. Perform continuity check on cabling. If rotator is moving, try to increase the value of Following Error Threshold in configuration file. Also, check the Current Output Limited light in the Manufacturer Status section on the Drive Status in EUI. A Current Output Limited light indicates a motor is trying to pull more current than the motor drive current limit. This could be caused by motor phasing problem if motor recently replaced or wear and/or environmental conditions causing the motor to draw more current than during acceptance testing. Current limit in XE2 drives can be increased using CME2 program, but creates greater risk of damage if rotator ever runs into end stop. Once problem identified, transition out of fault state with clear-error command.
   * - Ethercat Not Ready
     - Ethercat communication interruption or failure.
     - Drives disabled, brakes applied, EUI shut down, wrapper restarted.
     - Ensure all ethercat cables between control computer and drives and between the drives themselves are plugged in and undamaged. Could also be a temporary loss of communication due to problem in motor drive or control PC. Likely cannot recover from ethercat problem without using netbooter to reboot both channels (control PC and motor drives).
   * - Simulink Fault
     - Fault sensed in simulink portion of control code.
     - Drives disabled, brakes applied, enters fault state.
     - Variety of causes and will usually be combined with other faults to indicate source of problem. Once problem identified, transition out of fault state with clear-error command.
   * - Drive Fault
     - Fault in one of Copley motor drives.
     - Drives disabled, brakes applied, enters fault state.
     - Variety of causes. See Manufacturer Status lights in Drive Status in EUI for more specifics on problem. Once problem identified, transition out of fault state with clear-error command. Can use CME2 to see specific faults and clear errors/reset drive if clear error unsuccessful. Note that drive faults normally exist on Copley BE2 drive because it is only be used to reach encoders (no power output).
   * - Over Voltage or Voltage Enabled
     - DC bus voltage on XE2 drive exceeds 400 VDC.
     - Drive disabled, brakes applied, and enters fault state.
     - Check input supply power voltage. Once voltage back in range, transition out of fault state with clear-error command.
   * - Under Voltage or Voltage Enabled
     - DC bus voltage on XE2 drive under 60 VDC.
     - Drive disabled, brakes applied, and enters fault state.
     - Check input supply power voltage. Check internal cabinet wiring. Once voltage back in range, transition out of fault state with clear-error command.
   * - Amplifier Over Temperature
     - Amplifier temperature exceeds 80 deg C.
     - Drive disabled, brakes applied, and enters fault state.
     - Check that cabinet cooling system is working. Check that amplifier fan is working. Once temperature drops below 80 deg C, transition out of fault state with clear-error command.
   * - Internal Limit
     - Current, velocity, acceleration limit or other internal drive limit reached.
     - Remains in Enabled state.
     - Reaching velocity and acceleration limits during large rotator moves is normal. Reaching current limits consistently may be cause for concern and could result in following errors.
   * - Linear Encoder Fault
     - Rotator linear encoder not connected or providing bad readings.
     - Drive disabled, brakes applied, and enters fault state.
     - Ensure 7403-C7000 encoder cables are connected and undamaged. Use CME2 to investigate BE2 drive and potentially clear error or reset drive. Check internal cabinet wiring. May need to cycle power to computer and motor drives using netBooter to clear fault.
   * - Feedback Error
     - Over current condition detected on the output of the internal +5 VDC supply used to power feedback. Encoder not connected or levels out of tolerance.
     - Drive disabled, brakes applied, and enters fault state.
     - Ensure encoder cables are connected and undamaged, specifically 7403-C5000. Use CME2 to investigate XE2 drive and potentially clear error or reset drive. Check internal cabinet wiring.
   * - Motor Phasing Error
     - Encoder-based phase angle does not agree with Hall switch states.
     - Drive disabled, brakes applied, and enters fault state.
     - Ensure encoder cables are connected and undamaged, specifically 7403-C5000. May occur if actuator is replaced or motor drives swapped. If so, perform auto-phasing routine using Copley CME2 program with XE2 drive.
   * - Data Flash CRC Failure
     - Amplifier detected corrupted flash data values on startup.
     - Drive disabled, brakes applied, and enters fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - Amplifier Internal Error
     - Amplifier failed its power-on selftest.
     - Drive disabled, brakes applied, and enters fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - FPGA Failure
     - Amplifier detected an FPGA failure.
     - Drive disabled, brakes applied, and enters fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - Short Circuit
     - Short circuit detected on the motor outputs.
     - Drive disabled, brakes applied, and enters fault state.
     - Check motor power cabling. Measure resistance across motor leads to determine if the short is in motor. Must restart control program to unlatch fault.
   * - Invalid Command
     - Invalid or out of range command issued.
     - Command not executed, does not transition to fault state.
     - Command may exceed acceptable limits. Command may not be allowed in current state/substate.
   * - Position Feedback Fault
     - Rotator position is outside of acceptable range limits.
     - Drive disabled, brakes applied, and enters fault state.
     - Send clear-error command to get out of fault state. May need to mask limit switches if also tripped a limit switch. Use position-set command to move system back within currently defined range limits. Ensure that reasonable range limits have been defined (ie. position max is larger than position min) and new defined range limits did not place the current position outside of the limits.
   * - Voltage Output Limited
     - Can't provide necessary voltage to meet demand.
     - Warning only, does not transition to fault state.
     - Likely indicates that the motor power cable is disconnected or has a bad connection. A following error will likely occur if motion of the rotator is commanded.
   * - At Velocity Limit
     - Rotator moving at maximum velocity.
     - None, this can be encountered during normal operation.
     - N/A
   * - At Acceleration Limit
     - Rotator moving at maximum acceleration.
     - None, this can be encountered during normal operation.
     - N/A
   * - Position Counts Wrapped
     - Encoder counts have rolled over.
     - None, this can be encountered during normal operation.
     - N/A

.. _lsst.ts.rotgui-error_motor_drive_faults:

Motor Drive Faults
==================

Motor drive faults and other problems can be explored through Copley’s CME2 program which
only runs in Windows.
To access this program on the delivered Thinkpads, go to **Applications** -> **System Tools** -> **Oracle VM Virtual Box**.
Click on the **start** button when the **Oracle VM VirtualBox Manager** opens up.
The username and password were both **dell** at time of shipping.
Click on the CME2 icon to start the program and there will be access to all of the Copley drives for any of the rotators connected to the network.
The program provides an interface to view motor drive status and settings information.
See the CME2 user manual for additional information.

Note that two different Copley drives are used with the rotator: one XE2 and one BE2.
The XE2 is the primary drive which receives the motor encoder feedback, limit switch and interlock signals,
and provides current to the motors.
The BE2 drive is solely used to read the linear encoders on the rotator.
All of the drive status information provided in the EUI and telemetry comes from the XE2 drive except for the Linear Encoder Fault which comes from BE2 drive.

.. warning::
  Changing any of the motor drives settings has the potential to cause unexpected behavior and could result in damage to hardware or personnel.

  Changes should only be made by authorized personnel who understand the implications of such changes.
