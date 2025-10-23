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
from lsst.ts.rotgui import (
    MAX_ACCELERATION,
    MAX_JERK,
    MAX_ROTATION,
    MAX_VELOCITY,
    CommandSource,
    Config,
    ControlPanel,
    Model,
)
from lsst.ts.xml.enums import MTRotator
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> ControlPanel:
    widget = ControlPanel(Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: ControlPanel) -> None:
    assert widget._command_parameters["position"].maximum() == MAX_ROTATION
    assert widget._command_parameters["position"].minimum() == -MAX_ROTATION

    assert widget._command_parameters["velocity"].maximum() == MAX_VELOCITY
    assert widget._command_parameters["velocity"].minimum() == -MAX_VELOCITY

    assert widget._command_parameters["limit_velocity"].maximum() == MAX_VELOCITY
    assert widget._command_parameters["limit_acceleration"].maximum() == MAX_ACCELERATION
    assert widget._command_parameters["limit_jerk"].maximum() == MAX_JERK


@pytest.mark.asyncio
async def test_callback_command(qtbot: QtBot, widget: ControlPanel) -> None:
    # Single command parameter
    qtbot.mouseClick(widget._commands["enabled_substate"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["state"].isEnabled() is False
    assert widget._command_parameters["enabled_substate"].isEnabled() is True
    assert widget._command_parameters["position"].isEnabled() is False
    assert widget._command_parameters["velocity"].isEnabled() is False
    assert widget._command_parameters["duration"].isEnabled() is False

    # Two command parameters
    qtbot.mouseClick(widget._commands["velocity"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["state"].isEnabled() is False
    assert widget._command_parameters["enabled_substate"].isEnabled() is False
    assert widget._command_parameters["position"].isEnabled() is False
    assert widget._command_parameters["velocity"].isEnabled() is True
    assert widget._command_parameters["duration"].isEnabled() is True


def test_get_selected_command(widget: ControlPanel) -> None:
    for name, command in widget._commands.items():
        command.setChecked(True)

        assert widget._get_selected_command() == name


def test_update_fault_status(widget: ControlPanel) -> None:
    widget._update_fault_status(True)
    assert widget._indicators["fault"].text() == "Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.red

    widget._update_fault_status(False)
    assert widget._indicators["fault"].text() == "Not Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.green


@pytest.mark.asyncio
async def test_set_signal_state(widget: ControlPanel) -> None:
    command_source = CommandSource.CSC
    state = MTRotator.ControllerState.FAULT
    enabled_substate = MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT
    fault_substate = MTRotator.FaultSubstate.EMERGENCY_STOPPING

    widget.model.report_state(command_source, state, enabled_substate, fault_substate)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels["source"].text() == command_source.name
    assert widget._labels["state"].text() == state.name
    assert widget._labels["enabled_substate"].text() == enabled_substate.name
    assert widget._labels["fault_substate"].text() == fault_substate.name

    assert widget._indicators["fault"].text() == "Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.red


@pytest.mark.asyncio
async def test_set_signal_position_velocity(widget: ControlPanel) -> None:
    widget.model.report_position_velocity(10.1, 20.2, 30.3, 40.4)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels["position"].text() == "10.1000000"
    assert widget._labels["odometer"].text() == "30.3000000"


@pytest.mark.asyncio
async def test_set_signal_config(widget: ControlPanel) -> None:
    config = Config()
    config.velocity_limit = 0.1
    config.accel_limit = 0.2
    config.emergency_accel_limit = 0.3
    config.emergency_jerk_limit = 0.4
    config.drives_enabled = True

    widget.model.report_config(config)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["limit_velocity"].value() == 0.1
    assert widget._command_parameters["limit_acceleration"].value() == 0.2
    assert widget._command_parameters["emergency_acceleration"].value() == 0.3
    assert widget._command_parameters["emergency_jerk"].value() == 0.4

    assert widget._indicators["drive"].text() == "On"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.green


def test_update_drive_status(widget: ControlPanel) -> None:
    widget._update_drive_status(True)
    assert widget._indicators["drive"].text() == "On"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.green

    widget._update_drive_status(False)
    assert widget._indicators["drive"].text() == "Off"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.gray
