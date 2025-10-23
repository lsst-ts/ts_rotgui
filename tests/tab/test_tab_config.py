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

import asyncio
import logging

import pytest
from lsst.ts.rotgui import Config, Model
from lsst.ts.rotgui.tab import TabConfig
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabConfig:
    widget = TabConfig("Config", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_set_signal_config(widget: TabConfig) -> None:
    config = Config()
    config.velocity_limit = 1.1
    config.accel_limit = 2.2
    config.pos_error_threshold = 3.3
    config.upper_pos_limit = 4.4
    config.lower_pos_limit = 5.5
    config.following_error_threshold = 6.6
    config.track_success_pos_threshold = 7.7
    config.tracking_lost_timeout = 8.8
    config.emergency_jerk_limit = 9.9
    config.emergency_accel_limit = 10.1
    config.disable_limit_max_time = 11.1
    config.max_velocity_limit = 12.2
    config.drives_enabled = True

    widget.model.report_config(config)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._configuration["velocity_limit"].text() == "1.1 deg/sec"
    assert widget._configuration["acceleration_limit"].text() == "2.2 deg/sec^2"
    assert widget._configuration["position_error_threshold"].text() == "3.3 deg"
    assert widget._configuration["upper_position_limit"].text() == "4.4 deg"
    assert widget._configuration["lower_position_limit"].text() == "5.5 deg"
    assert widget._configuration["following_error_threshold"].text() == "6.6 deg"
    assert widget._configuration["tracking_success_threshold"].text() == "7.7 deg"
    assert widget._configuration["tracking_lost_timeout"].text() == "8.8 sec"
    assert widget._configuration["emergency_jerk_limit"].text() == "9.9 deg/sec^3"
    assert widget._configuration["emergency_acceleration_limit"].text() == "10.1 deg/sec^2"
    assert widget._configuration["disable_limit_max_time"].text() == "11.1 sec"
    assert widget._configuration["max_velocity_limit"].text() == "12.2 deg/sec"
    assert widget._configuration["drives_enabled"].text() == "<font color='green'>True</font>"
