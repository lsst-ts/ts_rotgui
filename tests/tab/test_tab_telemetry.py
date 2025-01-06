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
from lsst.ts.rotgui.tab import TabTelemetry
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabTelemetry:
    widget = TabTelemetry("Telemetry", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabTelemetry) -> None:

    assert len(widget._indicators["application_status"]) == 16
    assert len(widget._indicators["simulink_flag"]) == 11


@pytest.mark.asyncio
async def test_set_signal_application_status(widget: TabTelemetry) -> None:

    widget.model.report_application_status(0xFFFF, 0x7FF)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx, indicator in enumerate(widget._indicators["application_status"]):
        if idx in [0, 5, 6, 7, 8, 9, 11, 13, 14, 15]:
            assert indicator.palette().color(QPalette.Base) == Qt.red
        else:
            assert indicator.palette().color(QPalette.Base) == Qt.green

    for idx, indicator in enumerate(widget._indicators["simulink_flag"]):
        if idx in [5, 8, 9, 10]:
            assert indicator.palette().color(QPalette.Base) == Qt.red
        else:
            assert indicator.palette().color(QPalette.Base) == Qt.green


@pytest.mark.asyncio
async def test_set_signal_config(widget: TabTelemetry) -> None:

    config = Config(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1, 11.1, 12.2, True)
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
    assert (
        widget._configuration["emergency_acceleration_limit"].text() == "10.1 deg/sec^2"
    )
    assert widget._configuration["disable_limit_max_time"].text() == "11.1 sec"
    assert widget._configuration["max_velocity_limit"].text() == "12.2 deg/sec"
    assert (
        widget._configuration["drives_enabled"].text()
        == "<font color='green'>True</font>"
    )


@pytest.mark.asyncio
async def test_set_signal_control(widget: TabTelemetry) -> None:

    widget.model.report_control_data([11.1, 22.2], [33.3, 44.4], [55.5, 66.6], 77.7)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._telemetry["rate_command_a"].text() == "11.1000000 deg/sec"
    assert widget._telemetry["rate_command_b"].text() == "22.2000000 deg/sec"

    assert widget._telemetry["rate_feedback_a"].text() == "33.3000000 deg/sec"
    assert widget._telemetry["rate_feedback_b"].text() == "44.4000000 deg/sec"

    assert widget._telemetry["motor_torque_a"].text() == "55.5000000 N*m"
    assert widget._telemetry["motor_torque_b"].text() == "66.6000000 N*m"

    assert widget._telemetry["time_frame_difference"].text() == "77.7000000 sec"


@pytest.mark.asyncio
async def test_set_signal_position_velocity(widget: TabTelemetry) -> None:

    widget.model.report_position_velocity(10.1, 20.2, 30.3, 40.4)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._telemetry["position_current"].text() == "10.1000000 deg"
    assert widget._telemetry["position_command"].text() == "20.2000000 deg"
