# This file is part of ts_rotgui.
#
# Developed for the Vera Rubin Observatory Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = [
    "SignalState",
    "SignalApplicationStatus",
    "SignalPositionVelocity",
    "SignalPower",
    "SignalControl",
    "SignalDrive",
    "SignalConfig",
]

from PySide6 import QtCore


class SignalState(QtCore.QObject):
    """State signal to send the current controller's state."""

    # Command source, enum of `CommandSource`
    command_source = QtCore.Signal(int)

    # Controller's state, enum of `lsst.ts.xml.enums.MTRotator.ControllerState`
    state = QtCore.Signal(int)

    # Enabled substate, enum of `lsst.ts.xml.enums.MTRotator.EnabledSubstate`
    substate_enabled = QtCore.Signal(int)

    # Fault substate, enum of `lsst.ts.xml.enums.MTRotator.FaultSubstate`
    substate_fault = QtCore.Signal(int)


class SignalApplicationStatus(QtCore.QObject):
    """Application-status signal to send the current application status and
    Simulink flags."""

    # Application status
    status = QtCore.Signal(int)

    # Simulink flag
    simulink_flag = QtCore.Signal(int)


class SignalPositionVelocity(QtCore.QObject):
    """Position-velocity signal to send the current position and velocity of
    rotator."""

    # Current position in degrees
    position_current = QtCore.Signal(float)

    # Commanded position in degrees
    position_command = QtCore.Signal(float)

    # Odometer in degrees
    odometer = QtCore.Signal(float)

    # Velocity in deg/sec
    velocity = QtCore.Signal(float)


class SignalPower(QtCore.QObject):
    """Power signal to send the current current and voltage."""

    # Currents of [axis_a, axis_b] in ampere
    current = QtCore.Signal(object)

    # Bus voltage in volts
    voltage = QtCore.Signal(float)


class SignalControl(QtCore.QObject):
    """Control signal to send the commands of the actuators."""

    # Commanded rates of [axia_a, axis_b] in deg/sec
    rate_command = QtCore.Signal(object)

    # Feedback rates of [axia_a, axis_b] in deg/sec
    rate_feedback = QtCore.Signal(object)

    # Torque of [axia_a, axis_b] in N*m
    torque = QtCore.Signal(object)

    # Time frame difference in seconds
    time_difference = QtCore.Signal(float)


class SignalDrive(QtCore.QObject):
    """Drive signal to sent the current drive status."""

    # Status word of [axia_a, axis_b]
    status_word = QtCore.Signal(object)

    # Latching fault status of [axia_a, axis_b]
    latching_fault = QtCore.Signal(object)

    # Copley drive status of [axia_a, axis_b]
    copley_status = QtCore.Signal(object)

    # Input pin status of [axia_a, axis_b]
    input_pin = QtCore.Signal(object)


class SignalConfig(QtCore.QObject):
    """Configuration signal to send the current configuration."""

    # Instance of `Config` class
    config = QtCore.Signal(object)
