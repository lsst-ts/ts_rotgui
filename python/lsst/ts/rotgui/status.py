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

__all__ = ["Status"]

from dataclasses import dataclass, field

from .constants import NUM_STRUT


@dataclass
class Status:
    """System status."""

    # Telemetry timestamp
    timestamp: float = 0.0

    # Command source (enum `CommandSource`)
    command_source: int = 0

    # State (enum `lsst.ts.xml.enums.MTRotator.ControllerState`)
    state: int = 0

    # Enabled substate (enum `lsst.ts.xml.enums.MTRotator.EnabledSubstate`)
    substate_enabled: int = 0

    # Fault substate (enum `lsst.ts.xml.enums.MTRotator.FaultSubstate`)
    substate_fault: int = 0

    # Flag
    application_status: int = 0
    simulink_flag: int = 0

    # Drive
    status_word: list[int] = field(default_factory=lambda: [0] * NUM_STRUT)
    latching_fault: list[int] = field(default_factory=lambda: [0] * NUM_STRUT)
    copley_status: list[int] = field(default_factory=lambda: [0] * NUM_STRUT)
    input_pin: int = 0
