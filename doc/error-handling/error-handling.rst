.. _Error_Handling:

################
Error Handling
################

For the normal troubling shooting, refer to the :ref:`lsst.ts.hexgui-error_troubleshooting`.
In some cases, you may need to debug the Copley drive directly.
See the :ref:`lsst.ts.hexgui-error_motor_drive_faults` for more information.

.. _lsst.ts.hexgui-error_troubleshooting:

Troubleshooting
===============

This section provides a guide to identify and troubleshoot potential problems that may occur with the hexapods:

.. list-table:: Troubleshooting
   :widths: 30 70 70 120
   :header-rows: 1

   * - Fault
     - Errors Detected
     - Fault Condition
     - Recovery Procedure
   * - Safety Interlock
     - Safe Torque Off engaged on Copley XE2 drives due to safety interlock being activated (or not connected), rotator locking pin inserted, electrical cabinet power cycled, or internal wiring problem in cabinet.
     - Drives disabled, enter fault state, no ability to output torque.
     - Ensure safety interlock cable is connected (7403-C8200). Check that all safety interlock disable switches have been closed and reset switch has been cycled (always necessary on power-up). If both of the redundant disable signals were not activated and reclosed, safety relay will not reset and will display a fault. Check display lights on Pilz S4 and S7 relays and consult Pilz user manuals. Check internal cabinet wiring to safety relays. Once safety interlock fault cleared, transition out of fault state with clear-error state command.
   * - Positive Limit Switch
     - Extension limit switch activated, wiring problem, or switch failure.
     - Drives disabled, enter fault state, motion not allowed in positive/extending actuator direction while switch remains tripped.
     - Check telemetry to determine if actuator position has exceeded +14.1mm. If so, the switch is likely tripped. To move back off switch, send the mask-limit-switch command and send clear-error command to move out of fault state. Use set-raw-position command to move individual actuator off the switch. Investigate how software limits were exceeded. If the actuator position does not exceed +14.1mm, remove limit switch access cover on actuator to visually inspect switch. Finally, check cabinet and cable wiring.
   * - Negative Limit Switch
     - Retraction limit switch activated, wiring problem, or switch failure.
     - Drives disabled, enter fault state, motion not allowed in negative/retracting actuator direction while switch remains tripped.
     - Check telemetry to determine if actuator position has exceeded -14.1mm. If so, the switch is likely tripped. To move back off switch, send the mask-limit-switch command and send clear-error command to move out of fault state. Use set-raw-position command to move individual actuator off the switch. Investigate how software limits were exceeded. If the actuator position does not exceed -14.1mm, remove limit switch access cover on actuator to visually inspect switch. Finally, check cabinet and cable wiring.
   * - Following Error
     - Actuator position deviated from commanded position by more than threshold value indicating actuator is not moving at all or not moving at expected rate.
     - Motion of all actuators is stopped, drives disabled, and enter fault state.
     - If actuator did not appear to move at all, check to ensure that the motor power cables (7403-C1000) are connected to the correct actuator. Perform continuity check on cabling. If actuator is not moving at the expected rate, check the Current Output Limited light in the Manufacturer Status section on the Drive Status in GUI. A Current Output Limited light indicates the actuator is trying to pull more current than the motor drive current limit. This could be caused by motor phasing problem if actuator recently replaced or wear and/or environmental conditions causing the actuator to draw more current than during acceptance testing. Current limit in XE2 drives can be increased using CME2 program, but creates greater risk of damage if actuator ever runs into end stop. Following error limit could also be increased in the motor drive (set over ethercat) if errors increase over time. Once problem identified, transition out of fault state with clear-error state command.
   * - Ethercat Not Ready
     - Ethercat communication interruption or failure.
     - Drives disabled,motion stopped, GUI shut down, wrapper restarted.
     - Ensure all ethercat cables between control computer and drives and between the drives themselves are plugged in and undamaged. Could also be a temporary loss of communication due to problem in motor drive or control PC. Likely cannot recover from ethercat problem without using netbooter to reboot both channels (control PC and motor drives).
   * - Simulink Fault
     - Fault sensed in simulink portion of control code.
     - Drives disabled, motion stopped, enters fault state.
     - Variety of causes and will usually be combined with other faults to indicate source of problem. Once problem identified, transition out of fault state with clear-error state command.
   * - Drive Fault
     - Fault in one of Copley motor drives.
     - Drives disabled, motion stopped, enters fault state.
     - Variety of causes. See Manufacturer Status lights in Drive Status in GUI for more specifics on problem. Once problem identified, transition out of fault state with clear-error state command. Can use CME2 to see specific faults and clear errors/reset drive if clear-error state command is unsuccessful.
   * - Over Voltage
     - DC bus voltage exceeds 400 VDC.
     - Drive disabled and enters fault state.
     - Check input supply power voltage. Once voltage back in range, transition out of fault state with clear-error state command.
   * - Under Voltage
     - DC bus voltage under 60 VDC.
     - Drive disabled and enters fault state.
     - Check input supply power voltage. Check internal cabinet wiring. Once voltage back in range, transition out of fault state with clear-error state command.
   * - Amplifier Over Temperature
     - Amplifier temperature exceeds 80 deg C.
     - Drive disabled and enters fault state.
     - Check that cabinet cooling system is working. Check that amplifier fan is working. Once temperature drops below 80 deg C, transition out of fault state with clear-error state command.
   * - Internal Limit
     - Current, velocity, acceleration limit or other internal drive limit reached.
     - Remains in Enabled state.
     - Reaching velocity and acceleration limits during large hexapod moves is normal. Reaching current limits consistently may be cause for concern and could result in following errors. May need to increase current limit through CME2.
   * - Feedback Error
     - Over current condition detected on the output of the internal +5VDC supply used to power feedback. Encoder not connected or levels out of tolerance.
     - Drives disabled, enter fault state, latched fault.
     - Ensure encoder cables are connected and undamaged, specifically 7403-C3000. Check internal cabinet wiring. Must reboot control computer and motor drives using netBooter to unlatch fault.
   * - Motor Phasing Error
     - Encoder-based phase angle does not agree with Hall switch states.
     - Drives disabled, enter fault state.
     - Ensure encoder cables are connected and undamaged, specifically 7403-C2000. May occur if actuator is replaced or motor drives swapped. If so, perform auto-phasing routine using Copley CME2 program.
   * - Data Flash CRC Failure
     - Amplifier detected corrupted flash data values on startup.
     - Drives disabled, enter fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - Amplifier Internal Error
     - Amplifier failed its power-on self-test.
     - Drives disabled, enter fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - FPGA Failure
     - Amplifier detected a FPGA failure.
     - Drives disabled, enter fault state.
     - Fault cannot be cleared. Contact Copley for support.
   * - Short Circuit
     - Short circuit detected on the motor outputs.
     - Drives disabled, enter fault state.
     - Check motor power cabling. Measure resistance across motor leads to determine if the short is in motor. Must reboot control computer and motor drives using netBooter to unlatch fault.
   * - Motion Timeout
     - One or more actuators not completing move in expected amount of time, likely due to settling problem or extremely small commanded motion less than actuators resolution.
     - Drives remain enabled, does not transition to fault state.
     - Ensure that commanded motion was equal or greater than the hexapod's resolution specifications. If this alert is seen consistently for motions larger than the hexapod's resolution, PID gains may need to be adjusted in motor drives. If no motion occurs for moves that should be larger than the hexapod's resolution, ensure that all actuator motor power cables are connected properly (would likely be accompanied by a following error).
   * - Invalid Command
     - Invalid or out of range command issued.
     - Command not executed, does not transition to fault state.
     - Command may exceed acceptable limits. Command may not be allowed in current state/substate.
   * - Voltage Output Limited
     - Can't provide necessary voltage to meet demand.
     - Warning only, does not transition to fault state.
     - Likely indicates that the motor power cable is disconnected or has a bad connection. A following error will likely occur if motion of the hexapod is commanded.
   * - At Velocity Limit
     - Actuator moving at maximum velocity.
     - None, this can be encountered during normal operation.
     - N/A
   * - At Acceleration Limit
     - Actuator moving at maximum acceleration.
     - None, this can be encountered during normal operation.
     - N/A
   * - Position Counts Wrapped
     - Encoder counts have rolled over.
     - None, this can be encountered during normal operation.
     - N/A

.. _lsst.ts.hexgui-error_motor_drive_faults:

Motor Drive Faults
==================

Motor drive faults and other problems can be explored through Copley’s CME2 program which
only runs in Windows.
To access this program on the delivered Thinkpads, go to **Applications** -> **System Tools** -> **Oracle VM Virtual Box**.
Click on the **start** button when the **Oracle VM VirtualBox Manager** opens up.
The username and password were both **dell** at time of shipping.
Click on the CME2 icon to start the program and there will be access to all of the Copley drives for any of the hexapods connected to the network.
The program provides an interface to view motor drive status and settings information.
See the CME2 user manual for additional information.

Note that the hexapod uses three Copley XE2 drives.
XE2 #1 controls actuators 1 and 2 on channels A and B, respectively.
XE2 #2 controls actuators 3 and 4 on channels A and B, respectively.
XE2 #3 controls actuators 5 and 6 on channels A and B, respectively.

.. warning::
  Changing any of the motor drives settings has the potential to cause unexpected behavior and could result in damage to hardware or personnel.

  Changes should only be made by authorized personnel who understand the implications of such changes.
