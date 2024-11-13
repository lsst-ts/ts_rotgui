# This file is part of ts_rotgui.
#
# Developed for the LSST Telescope and Site Systems.
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

__all__ = ["CommandSource", "TriggerState", "TriggerEnabledSubState"]

from enum import IntEnum, auto


class CommandSource(IntEnum):
    """Command source."""

    GUI = 1
    CSC = auto()


class TriggerState(IntEnum):
    """Trigger to do the state transition.

    Notes
    -----
    The value is different from the parameter to the controller.
    """

    Enable = 1  # Parameter to controller is 2
    StandBy = auto()  # Parameter to controller is 3
    ClearError = auto()  # Parameter to controller is 6


class TriggerEnabledSubState(IntEnum):
    """Trigger to do the enabled sub-state transition.

    Notes
    -----
    The value is different from the parameter to the controller.
    """

    Move = 1  # Parameter to controller is 1
    Stop = auto()  # Parameter to controller is 3
    MoveConstantVel = auto()  # Parameter to controller is 6
