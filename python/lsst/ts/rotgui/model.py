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

__all__ = ["Model"]

import logging
import typing

from lsst.ts.xml.enums import MTRotator
from PySide6.QtCore import Signal

from .config import Config
from .constants import NUM_STRUT
from .enums import CommandSource
from .signals import (
    SignalApplicationStatus,
    SignalConfig,
    SignalControl,
    SignalDrive,
    SignalPositionVelocity,
    SignalPower,
    SignalState,
)
from .status import Status


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    host : `str`, optional
        Host address. (the default is "localhost")
    port : `int`, optional
        Port to connect. (the default is 5570)
    timeout_connection : `float`, optional
        Connection timeout in second. (the default is 10.0)
    is_simulation_mode: `bool`, optional
        True if running in simulation mode. (the default is False)
    duration_refresh : `int`, optional
        Duration to refresh the data in milliseconds. (the default is 100)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    connection_information : `dict`
        TCP/IP connection information.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    signals : `dict`
        Signals.
    """

    def __init__(
        self,
        log: logging.Logger,
        host: str = "localhost",
        port: int = 5570,
        timeout_connection: float = 10.0,
        is_simulation_mode: bool = False,
        duration_refresh: int = 100,
    ) -> None:

        self.log = log

        self.connection_information = {
            "host": host,
            "port": port,
            "timeout_connection": timeout_connection,
        }

        self._is_simulation_mode = is_simulation_mode
        self.duration_refresh = duration_refresh

        self._status = Status()

        self.signals = {
            "state": SignalState(),
            "application_status": SignalApplicationStatus(),
            "drive": SignalDrive(),
            "config": SignalConfig(),
            "control": SignalControl(),
            "position_velocity": SignalPositionVelocity(),
            "power": SignalPower(),
        }

    def report_default(self) -> None:
        """Report the default status."""

        signal_state = self.signals["state"]
        signal_state.command_source.emit(  # type: ignore[attr-defined]
            CommandSource.GUI.value
        )
        signal_state.state.emit(  # type: ignore[attr-defined]
            MTRotator.ControllerState.STANDBY.value
        )
        signal_state.substate_enabled.emit(  # type: ignore[attr-defined]
            MTRotator.EnabledSubstate.STATIONARY.value
        )
        signal_state.substate_fault.emit(  # type: ignore[attr-defined]
            MTRotator.FaultSubstate.NO_ERROR.value
        )

        signal_drive = self.signals["drive"]
        signal_drive.status_word.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.latching_fault.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.copley_status.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.input_pin.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]

        signal_application_status = self.signals["application_status"]
        signal_application_status.status.emit(0)  # type: ignore[attr-defined]
        signal_application_status.simulink_flag.emit(0)  # type: ignore[attr-defined]

        self.report_config(Config())
        self.report_control_data(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0
        )
        self.report_position_velocity(0.0, 0.0, 0.0, 0.0)

    def report_config(self, config: Config) -> None:
        """Report the configuration.

        Parameters
        ----------
        config : `Config`
            Configuration details.
        """

        self.signals["config"].config.emit(config)  # type: ignore[attr-defined]

    def report_control_data(
        self,
        rate_command: list[float],
        rate_feedback: list[float],
        torque: list[float],
        time_difference: float,
    ) -> None:
        """Report the control data.

        Parameters
        ----------
        rate_command : `list` [`float`]
            Commanded rates of [axia_a, axis_b] in deg/sec.
        rate_feedback : `list` [`float`]
            Feedback rates of [axia_a, axis_b] in deg/sec.
        torque : `list` [`float`]
            Torque of [axia_a, axis_b] in N*m.
        time_difference : `float`
            Time frame difference in seconds.
        """

        signal = self.signals["control"]
        signal.rate_command.emit(rate_command)  # type: ignore[attr-defined]
        signal.rate_feedback.emit(rate_feedback)  # type: ignore[attr-defined]
        signal.torque.emit(torque)  # type: ignore[attr-defined]
        signal.time_difference.emit(time_difference)  # type: ignore[attr-defined]

    def report_position_velocity(
        self,
        position_current: float,
        position_command: float,
        odometer: float,
        velocity: float,
    ) -> None:
        """Report the position and velocity.

        Parameters
        ----------
        position_current : `float`
            Current position in degrees.
        position_command : `float`
            Commanded position in degrees.
        odometer : `float`
            Odometer in degrees.
        velocity : `float`
            Velocity in deg/sec.
        """

        signal = self.signals["position_velocity"]
        signal.position_current.emit(position_current)  # type: ignore[attr-defined]
        signal.position_command.emit(position_command)  # type: ignore[attr-defined]
        signal.odometer.emit(odometer)  # type: ignore[attr-defined]
        signal.velocity.emit(velocity)  # type: ignore[attr-defined]

    def report_power(self, current: list[float], voltage: float) -> None:
        """Report the power.

        Parameters
        ----------
        current : `list` [`float`]
            Currents of [axis_a, axis_b] in ampere.
        voltage : `float`
            Voltage in volts.
        """

        signal = self.signals["power"]
        signal.current.emit(current)  # type: ignore[attr-defined]
        signal.voltage.emit(voltage)  # type: ignore[attr-defined]

    def report_state(
        self,
        command_source: CommandSource,
        state: MTRotator.ControllerState,
        substate_enabled: MTRotator.EnabledSubstate,
        substate_fault: MTRotator.FaultSubstate,
    ) -> None:
        """Report the controller's state.

        Parameters
        ----------
        command_source : enum `CommandSource`
            Command source.
        state : enum `MTRotator.ControllerState`
            State.
        substate_enabled : enum `MTRotator.EnabledSubstate`
            Enabled substate.
        substate_fault : enum `MTRotator.FaultSubstate`
            Fault substate.
        """

        signal = self.signals["state"]

        self._compare_status_and_report(
            "command_source",
            command_source.value,
            signal.command_source,  # type: ignore[attr-defined]
        )
        self._compare_status_and_report("state", state.value, signal.state)  # type: ignore[attr-defined]
        self._compare_status_and_report(
            "substate_enabled", substate_enabled.value, signal.substate_enabled  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "substate_fault", substate_fault.value, signal.substate_fault  # type: ignore[attr-defined]
        )

    def _compare_status_and_report(
        self, field: str, value: typing.Any, signal: Signal
    ) -> None:
        """Compare the value with current status and report it if different.

        Parameters
        ----------
        field : `str`
            Field of the status.
        value : `typing.Any`
            Value.
        signal : `PySide6.QtCore.Signal`
            Signal.

        Raises
        ------
        `TypeError`
            When the type of value does not match with the type of status's
            value.
        """

        status_value = getattr(self._status, field)
        if type(value) is not type(status_value):
            raise TypeError(
                f"Type of value ({type(value)}) does not match with type of "
                f"status's value ({type(status_value)})."
            )

        if value != status_value:
            signal.emit(value)
            setattr(self._status, field, value)

    def report_application_status(self, status: int, simulink_flag: int) -> None:
        """Report the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        simulink_flag : `int`
            Simulink flag.
        """

        signal = self.signals["application_status"]

        self._compare_status_and_report(
            "application_status", status, signal.status  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "simulink_flag", simulink_flag, signal.simulink_flag  # type: ignore[attr-defined]
        )

    def report_drive_status(
        self,
        status_word: list[int],
        latching_fault: list[int],
        copley_status: list[int],
        input_pin: list[int],
    ) -> None:
        """Report the drive status.

        Parameters
        ----------
        status_word : `list` [`int`]
            Status word of [axia_a, axis_b].
        latching_fault : `list` [`int`]
            Latching fault status of [axia_a, axis_b].
        copley_status : `list` [`int`]
            Copley drive status of [axia_a, axis_b].
        input_pin : `list` [`int`]
            Input pin status of [axia_a, axis_b].
        """

        signal = self.signals["drive"]

        self._compare_status_and_report(
            "status_word", status_word, signal.status_word  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "latching_fault", latching_fault, signal.latching_fault  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "copley_status", copley_status, signal.copley_status  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "input_pin", input_pin, signal.input_pin  # type: ignore[attr-defined]
        )
