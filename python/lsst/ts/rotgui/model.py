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

import asyncio
import logging
import types
import typing

from lsst.ts.hexrotcomm import Command, CommandTelemetryClient
from lsst.ts.tcpip import LOCALHOST_IPV4
from lsst.ts.xml.enums import MTRotator
from PySide6.QtCore import Signal

from .constants import NUM_STRUT
from .enums import CommandCode, CommandSource, TriggerEnabledSubState, TriggerState
from .mock_controller import MockController
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
from .structs import Config, Telemetry


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    host : `str`, optional
        Host address. (the default is LOCALHOST_IPV4)
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
    client : `lsst.ts.hexrotcomm.CommandTelemetryClient` or None
        Command and telemetry client. (the default is None)
    """

    def __init__(
        self,
        log: logging.Logger,
        host: str = LOCALHOST_IPV4,
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
        self._mock_ctrl: MockController | None = None

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

        self.client: CommandTelemetryClient | None = None

    def is_connected(self) -> bool:
        """Check if the client is connected.

        Returns
        -------
        `bool`
            True if the client is connected.
        """

        return (self.client is not None) and self.client.connected

    async def connect(self) -> None:
        """Connect to the low-level controller.

        Raises
        ------
        `RuntimeError`
            If the connection times out or is refused.
        """

        await self.disconnect()

        try:
            if self._is_simulation_mode:
                self._mock_ctrl = MockController(
                    self.log,
                )
                await self._mock_ctrl.start_task

                host = LOCALHOST_IPV4
                port = self._mock_ctrl.port

            else:
                host = self.connection_information["host"]
                port = self.connection_information["port"]

            self.log.info(f"Connecting to {host}:{port}.")

            self.client = CommandTelemetryClient(
                log=self.log,
                ConfigClass=Config,
                TelemetryClass=Telemetry,
                host=host,
                port=port,
                connect_callback=self.connect_callback,
                config_callback=self.config_callback,
                telemetry_callback=self.telemetry_callback,
            )

            await asyncio.wait_for(
                self.client.start_task,
                timeout=self.connection_information["timeout_connection"],  # type: ignore[arg-type]
            )

        except asyncio.TimeoutError:
            raise RuntimeError("Timed out while connecting to the controller")

        except ConnectionRefusedError:
            raise RuntimeError("Connection refused by the controller.")

        except Exception:
            raise

    async def disconnect(self) -> None:
        """Disconnect from the low-level controller."""

        # Close the client
        if self.is_connected():
            try:
                # Workaround the mypy check
                assert self.client is not None

                await self.client.close()

            except Exception:
                self.log.exception("disconnect(): self.client.close() failed")

        self.client = None

        # Close the mock controller
        if self._mock_ctrl is not None:
            try:
                await self._mock_ctrl.close()

            except Exception:
                self.log.exception("disconnect: self._mock_ctrl.close() failed")

        self._mock_ctrl = None

    async def connect_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the client socket connects or disconnects.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        if client.should_be_connected and not client.connected:
            self.log.error("Lost connection to the low-level controller")

        if client.connected:
            self.log.info("Connected to the low-level controller")
        else:
            self.log.info("Disconnected from the low-level controller")

    async def config_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the TCP/IP controller outputs configuration.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        self.report_config(client.config)

    async def telemetry_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the TCP/IP controller outputs telemetry.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        telemetry = client.telemetry

        # Report the control data
        # The torque from the low-level controller is N-m/1e6
        # (and is an integer); convert it to N-m
        timestamp = client.header.tai_sec + client.header.tai_nsec * 1e-9
        self.report_control_data(
            [telemetry.rate_cmd_ch_a, telemetry.rate_cmd_ch_b],
            [telemetry.current_vel_ch_a_fb, telemetry.current_vel_ch_b_fb],
            [telemetry.motor_torque_axis_a / 1e6, telemetry.motor_torque_axis_b / 1e6],
            timestamp - self._status.timestamp,
        )
        self._status.timestamp = timestamp

        # Report the position and velocity
        self.report_position_velocity(
            telemetry.current_pos,
            telemetry.demand_pos,
            telemetry.rotator_odometer,
            (telemetry.current_vel_ch_a_fb + telemetry.current_vel_ch_b_fb) / 2.0,
        )

        # Report the power
        self.report_power(telemetry.motor_current, telemetry.bus_voltage)

        # Report the state

        # See ts_rotator_controller repository for the enum value:
        # AppStatus_CommandByCsc = 0x400
        command_source = (
            CommandSource.CSC
            if (telemetry.application_status & 0x400)
            else CommandSource.GUI
        )
        self.report_state(
            command_source,
            MTRotator.ControllerState(telemetry.state),
            MTRotator.EnabledSubstate(telemetry.enabled_substate),
            MTRotator.FaultSubstate(telemetry.fault_substate),
        )

        # Report application status
        self.report_application_status(
            telemetry.application_status,
            self._get_simulink_flag(telemetry),
        )

        # Report drive status
        self.report_drive_status(
            [telemetry.status_word_drive0, telemetry.status_word_drive0_axis_b],
            [
                telemetry.latching_fault_status_register,
                telemetry.latching_fault_status_register_axis_b,
            ],
            list(telemetry.copley_fault_status_register),
            telemetry.input_pin_states,
        )

    def _get_simulink_flag(self, telemetry: Telemetry) -> int:
        """Get the simulink flag.

        Parameters
        ----------
        telemetry : `Telemetry`
            Telemetry.

        Returns
        -------
        simulink_flag : `int`
            Simulink flag.
        """

        flags = [
            "flags_initialization_complete",
            "flags_slew_complete",
            "flags_pt2pt_move_complete",
            "flags_new_pt2pt_command",
            "flags_stop_complete",
            "flags_following_error",
            "flags_move_success",
            "flags_tracking_success",
            "flags_position_feedback_fault",
            "flags_tracking_lost",
            "flags_no_new_track_cmd_error",
        ]

        simulink_flag = 0
        for idx, flag in enumerate(flags):
            if getattr(telemetry, flag) != 0.0:
                simulink_flag += 1 << idx

        return simulink_flag

    def is_csc_commander(self) -> bool:
        """Commandable SAL component (CSC) is the commander or not.

        Returns
        -------
        `bool`
            True if the CSC is the commander. False otherwise.
        """
        return self._status.command_source == CommandSource.CSC

    async def enable_drives(self, status: bool, time: float = 1.0) -> None:
        """Enable the drives.

        Parameters
        ----------
        status : `bool`
            True if enable the drives. Otherwise, False.
        time : `float`, optional
            Sleep time in second. (the default is 1.0)
        """

        self.assert_is_connected()

        # Workaround the mypy check
        assert self.client is not None

        command = self.make_command(CommandCode.ENABLE_DRIVES, param1=float(status))
        await self.client.run_command(command)

        await asyncio.sleep(time)

    def assert_is_connected(self) -> None:
        """Assert that the client is connected.

        Raises
        ------
        `RuntimeError`
            When the client is not connected.
        """

        if not self.is_connected():
            raise RuntimeError("Not connected to the low-level controller")

    def make_command(
        self,
        code: CommandCode,
        param1: float = 0.0,
        param2: float = 0.0,
        param3: float = 0.0,
        param4: float = 0.0,
        param5: float = 0.0,
        param6: float = 0.0,
    ) -> Command:
        """Make a command from the command identifier and keyword arguments.

        Parameters
        ----------
        code : enum `CommandCode`
            Command to run.
        param1, param2, param3, param4, param5, param6 : `double`, optional
            Command parameters. The meaning of these parameters
            depends on the command code.

        Returns
        -------
        command : `lsst.ts.hexrotcomm.Command`
            The command. Note that the `counter` field is 0;
            it is set by `CommandTelemetryClient.run_command`.
        """

        command = Command()

        # Set the commander to be GUI. See the enum "Commander" in
        # ts_hexrotpxicom.
        command.COMMANDER = 1

        command.code = code.value
        command.param1 = param1
        command.param2 = param2
        command.param3 = param3
        command.param4 = param4
        command.param5 = param5
        command.param6 = param6

        self.log.debug(
            f"New command: {code.name} ({hex(code.value)}): {param1=}, "
            f"{param2=}, {param3=}, {param4=}, {param5=}, {param6=}"
        )

        return command

    def make_command_state(self, trigger_state: TriggerState) -> Command:
        """Make the state command.

        Parameters
        ----------
        trigger_state : enum `TriggerState`
            Trigger state.

        Returns
        -------
        `lsst.ts.hexrotcomm.Command`
            State command.
        """

        if trigger_state == TriggerState.Enable:
            return self.make_command(CommandCode.SET_STATE, param1=2.0)
        elif trigger_state == TriggerState.StandBy:
            return self.make_command(CommandCode.SET_STATE, param1=3.0)
        else:
            # Should be the TriggerState.ClearError
            return self.make_command(CommandCode.SET_STATE, param1=6.0)

    def make_command_enabled_substate(
        self,
        trigger_enabled_substate: TriggerEnabledSubState,
    ) -> Command:
        """Make the enabled substate command.

        Parameters
        ----------
        trigger_enabled_substate : enum `TriggerEnabledSubState`
            Trigger enabled substate.

        Returns
        -------
        `lsst.ts.hexrotcomm.Command`
            Enabled substate command.
        """

        if trigger_enabled_substate == TriggerEnabledSubState.Move:
            return self.make_command(
                CommandCode.SET_ENABLED_SUBSTATE,
                param1=1.0,
            )
        elif trigger_enabled_substate == TriggerEnabledSubState.MoveConstantVel:
            return self.make_command(
                CommandCode.SET_ENABLED_SUBSTATE,
                param1=6.0,
            )
        else:
            # Should be the TriggerEnabledSubState.Stop
            return self.make_command(CommandCode.SET_ENABLED_SUBSTATE, param1=3.0)

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
        signal_drive.input_pin.emit(0x300C0)  # type: ignore[attr-defined]

        signal_application_status = self.signals["application_status"]
        signal_application_status.status.emit(0)  # type: ignore[attr-defined]
        signal_application_status.simulink_flag.emit(0)  # type: ignore[attr-defined]

        self.report_config(Config())
        self.report_control_data(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0
        )
        self.report_position_velocity(0.0, 0.0, 0.0, 0.0)

        self.report_power([0.0] * NUM_STRUT, 0.0)

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

            self.log.info(f"Update system status: {field} = {value}")

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
        input_pin: int,
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
        input_pin : `int`
            Input pin status.
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

    async def __aenter__(self) -> object:
        """This is an overridden function to support the asynchronous context
        manager."""
        return self

    async def __aexit__(
        self,
        type: typing.Type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.disconnect()
