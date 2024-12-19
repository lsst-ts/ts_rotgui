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

__all__ = ["Config"]

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class to have the configuration details."""

    # In deg/sec
    velocity_limit: float = 0.0

    # In deg/sec^2
    acceleration_limit: float = 0.0

    # In deg
    position_error_threshold: float = 0.0

    # In deg
    upper_position_limit: float = 0.0
    lower_position_limit: float = 0.0

    # In deg
    following_error_threshold: float = 0.0
    track_success_position_threshold: float = 0.0

    # In sec
    tracking_lost_timeout: float = 0.0

    # In deg/sec^3
    emergency_jerk_limit: float = 0.0

    # In deg/sec^2
    emergency_acceleration_limit: float = 0.0

    # In sec
    disable_limit_max_time: float = 0.0

    # In deg/sec
    max_velocity_limit: float = 0.0

    drives_enabled: bool = False
