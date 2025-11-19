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
    "CommandSource",
    "TriggerState",
    "TriggerEnabledSubState",
    "CommandCode",
]

from enum import IntEnum, auto


class CommandSource(IntEnum):
    """Command source."""

    GUI = 0  # To fit the low-level controller's definition
    CSC = auto()


class TriggerState(IntEnum):
    """Trigger to do the state transition.

    Notes
    -----
    The value is different from the parameter to the controller.
    """

    Enable = 0  # Parameter to controller is 2
    StandBy = auto()  # Parameter to controller is 3
    ClearError = auto()  # Parameter to controller is 6


class TriggerEnabledSubState(IntEnum):
    """Trigger to do the enabled sub-state transition.

    Notes
    -----
    The value is different from the parameter to the controller.
    """

    Move = 0  # Parameter to controller is 1
    Stop = auto()  # Parameter to controller is 3
    MoveConstantVel = auto()  # Parameter to controller is 6
    Track = auto()  # Parameter to controller is 2


class CommandCode(IntEnum):
    """Command code.

    In the low-level controller code these are defined in
    enum "CmdType".
    """

    DEFAULT = 0x0
    ENABLE_DRIVES = 0x7000
    SET_STATE = 0x8000
    SET_ENABLED_SUBSTATE = 0x8002
    POSITION_SET = 0x8007
    CMD_SOURCE = 0x8008
    MASK_LIMIT_SW = 0x800A
    SET_CONSTANT_VEL = 0x800B
    DISABLE_UPPER_POS_LIMIT = 0x800C
    DISABLE_LOWER_POS_LIMIT = 0x800D
    CONFIG_VEL = 0x9001
    CONFIG_ACCEL = 0x9002
    CONFIG_ACCEL_EMERGENCY = 0x9003
    CONFIG_JERK_EMERGENCY = 0x9004
    CONFIG_JERK = 0x9005
    TRACK_VEL_CMD = 0x9031
