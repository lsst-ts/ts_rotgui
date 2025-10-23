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

__all__ = ["MockController"]

import logging
import typing

import numpy as np
from lsst.ts.hexrotcomm import BaseMockController, Command
from lsst.ts.xml.enums import MTRotator

from .constants import MAX_ACCELERATION, MAX_JERK, MAX_ROTATION, MAX_VELOCITY, NUM_STRUT
from .enums import CommandCode
from .structs import Config, Telemetry


class MockController(BaseMockController):
    """Mock controller to simulate the controller behavior.

    Parameters
    ----------
    log : `logging.Logger`
        Logger.
    port : `int`, optional
        Command socket port. (the default is 0)
    initial_state : enum `MTRotator.ControllerState`, optional
        Initial state of the mock controller.
    """

    # Strut current (A) and bus voltage (V) as constants
    STRUT_CURRENT = 0.8
    BUS_VOLTAGE = 330.0

    # Move position "deg" per cycle
    CYCLE_MOVE_POSITION_DEG = 5.0

    def __init__(
        self,
        log: logging.Logger,
        port: int = 0,
        initial_state: MTRotator.ControllerState = MTRotator.ControllerState.STANDBY,
    ) -> None:
        extra_commands = {
            (
                CommandCode.SET_ENABLED_SUBSTATE,
                1,  # Move in the controller
            ): self.do_move_point_to_point,
            (
                CommandCode.SET_ENABLED_SUBSTATE,
                3,  # Stop in the controller
            ): self.do_stop,
            (
                CommandCode.SET_ENABLED_SUBSTATE,
                6,  # Constant velocity movement in the controller
            ): self.do_not_supported_command,
            CommandCode.POSITION_SET: self.do_position_set,
            CommandCode.SET_CONSTANT_VEL: self.do_not_supported_command,
            CommandCode.MASK_LIMIT_SW: self.do_not_supported_command,
            CommandCode.DISABLE_UPPER_POS_LIMIT: self.do_not_supported_command,
            CommandCode.DISABLE_LOWER_POS_LIMIT: self.do_not_supported_command,
            CommandCode.CMD_SOURCE: self.do_switch_command_source,
            CommandCode.CONFIG_VEL: self.do_config_vel,
            CommandCode.CONFIG_ACCEL: self.do_config_accel,
            CommandCode.CONFIG_JERK: self.do_not_supported_command,
            CommandCode.CONFIG_ACCEL_EMERGENCY: self.do_config_accel_emergency,
            CommandCode.CONFIG_JERK_EMERGENCY: self.do_config_jerk_emergency,
        }

        super().__init__(
            log=log,
            CommandCode=CommandCode,
            extra_commands=extra_commands,
            config=self._create_config(),
            telemetry=self._create_telemetry(),
            port=port,
            initial_state=initial_state,
        )

        # Whether the CSC is the commander
        self._is_csc_commander = False

        # Commanded rotator's position in degree.
        # If None, no position has been commanded.
        self._commanded_position: float | None = None

    def _create_config(self) -> Config:
        """Create the configuration.

        Returns
        -------
        config : `Config`
            Configuration.
        """

        config = Config()
        config.velocity_limit = MAX_VELOCITY
        config.accel_limit = MAX_ACCELERATION
        config.pos_error_threshold = 0.1  # deg
        config.lower_pos_limit = -MAX_ROTATION
        config.upper_pos_limit = MAX_ROTATION
        config.following_error_threshold = 0.1  # deg
        config.track_success_pos_threshold = 0.01  # deg
        config.tracking_lost_timeout = 5  # sec
        config.emergency_jerk_limit = MAX_JERK
        config.emergency_accel_limit = MAX_ACCELERATION
        config.disable_limit_max_time = 120  # sec
        config.max_velocity_limit = MAX_VELOCITY
        config.drives_enabled = False

        return config

    def _create_telemetry(self) -> Telemetry:
        """Create the telemetry.

        Returns
        -------
        telemetry : `Telemetry`
            Telemetry.
        """

        telemetry = Telemetry()
        telemetry.bus_voltage = self.BUS_VOLTAGE

        return telemetry

    async def do_move_point_to_point(self, command: Command) -> None:
        """Do the point-to-point movement.

        Parameters
        ----------
        command : `Command`
            Command.

        Raises
        ------
        `RuntimeError`
            When the position is not set.
        """

        self.assert_stationary()

        if self._commanded_position is None:
            raise RuntimeError("Must set the position first.")

        self.telemetry.demand_pos = self._commanded_position
        self.telemetry.enabled_substate = MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT

    async def do_stop(self, command: Command) -> None:
        """Stop the movement.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.telemetry.enabled_substate = MTRotator.EnabledSubstate.STATIONARY

    async def do_position_set(self, command: Command) -> None:
        """Set the position.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._commanded_position = command.param1

    async def do_not_supported_command(self, command: Command) -> None:
        """Not supported command.

        Parameters
        ----------
        command : `Command`
            Command.

        Raises
        ------
        `RuntimeError`
            Not supported in the simulator.
        """

        raise RuntimeError("Not supported in the simulator.")

    async def do_switch_command_source(self, command: Command) -> None:
        """Switch the command source.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self._is_csc_commander = command.param1 == 1.0

    async def do_config_accel(self, command: Command) -> None:
        """Configure the acceleration.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "acceleration", MAX_ACCELERATION)

        self.config.accel_limit = command.param1
        await self.write_config()

    def _check_positive_value(self, value: float, name: str, max_value: float) -> None:
        """Check that a numeric value is in range.

        Parameters
        ----------
        value : `float`
            Value to check.
        name : `str`
            Name of value.
        max_value : `float`
            Maximum allowed value of the named field (inclusive).

        Raises
        ------
        `RuntimeError`
            When the value is not in range.
        """

        if not 0 < value <= max_value:
            raise RuntimeError(f"{name}={value} not in range (0, {max_value}]")

    async def do_config_vel(self, command: Command) -> None:
        """Configure the velocity.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "velocity", MAX_VELOCITY)

        self.config.velocity_limit = command.param1
        await self.write_config()

    async def do_config_accel_emergency(self, command: Command) -> None:
        """Configure the emergency acceleration.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "emergency acceleration", MAX_ACCELERATION)

        self.config.emergency_accel_limit = command.param1
        await self.write_config()

    async def do_config_jerk_emergency(self, command: Command) -> None:
        """Configure the emergency jerk.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "emergency jerk", MAX_JERK)

        self.config.emergency_jerk_limit = command.param1
        await self.write_config()

    async def end_run_command(self, command: Command, cmd_method: typing.Coroutine) -> None:
        if cmd_method != self.do_position_set:
            self._commanded_position = None

    async def update_telemetry(self, curr_tai: float) -> None:
        try:
            # Copley drive status
            self.telemetry.latching_fault_status_register = 0
            self.telemetry.latching_fault_status_register_axis_b = 0

            self.telemetry.input_pin_states = 0x380E0

            self.telemetry.copley_fault_status_register = (0xF000,) * NUM_STRUT

            status_word = 0x631 if self.config.drives_enabled else 0x670
            self.telemetry.status_word_drive0 = status_word
            self.telemetry.status_word_drive0_axis_b = status_word

            # Application status
            self.telemetry.application_status = MTRotator.ApplicationStatus.EUI_CONNECTED
            if self._is_csc_commander:
                self.telemetry.application_status |= MTRotator.ApplicationStatus.DDS_COMMAND_SOURCE

            # Power
            self.telemetry.motor_current = (
                (self.STRUT_CURRENT,) * NUM_STRUT if self.config.drives_enabled else (0.0,) * NUM_STRUT
            )
            self.telemetry.bus_voltage = self.BUS_VOLTAGE

            # Rotator position
            if self.telemetry.enabled_substate == MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT:
                # Do the movement
                velocity = np.sign(self.telemetry.demand_pos - self.telemetry.current_pos) * MAX_VELOCITY
                is_done, new_position = self._move_position(
                    self.telemetry.current_pos,
                    self.telemetry.demand_pos,
                    self.CYCLE_MOVE_POSITION_DEG,
                )

                self.telemetry.current_pos = new_position
                self.telemetry.current_vel_ch_a_fb = 0.0 if is_done else velocity
                self.telemetry.current_vel_ch_b_fb = 0.0 if is_done else velocity

                # Change the substate if the movement is done
                if is_done:
                    self.telemetry.enabled_substate = MTRotator.EnabledSubstate.STATIONARY
                    self._commanded_position = None

        except Exception:
            self.log.exception("update_telemetry failed; output incomplete telemetry")

    def _move_position(
        self, position_current: float, position_target: float, step: float
    ) -> tuple[bool, float]:
        """Move the position.

        Parameters
        ----------
        position_current : `float`
            Current position.
        position_target : `float`
            Target position.
        step : `float`
            Step. Should be a positive value.

        Returns
        -------
        `tuple` [`bool`, `float`]
            Whether the movement is done and the new position. True if the
            movement is done. False otherwise.
        """

        # Return if the current position is already at the target position
        if position_current == position_target:
            return (True, position_current)

        # Determine the direction to move and calculate the new position
        direction = np.sign(position_target - position_current)
        position_new = position_current + direction * step

        # Check if the new position is at the target position
        if (direction > 0) and (position_new >= position_target):
            return (True, position_target)

        if (direction < 0) and (position_new <= position_target):
            return (True, position_target)

        # Return the new position
        return (False, position_new)
