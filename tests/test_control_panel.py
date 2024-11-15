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
from lsst.ts.rotgui import MAX_ROTATION, MAX_VELOCITY, ControlPanel, Model
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


def test_update_fault_status(widget: ControlPanel) -> None:

    widget._update_fault_status(True)
    assert widget._indicator_fault.text() == "Faulted"
    assert widget._indicator_fault.palette().color(QPalette.Button) == Qt.red

    widget._update_fault_status(False)
    assert widget._indicator_fault.text() == "Not Faulted"
    assert widget._indicator_fault.palette().color(QPalette.Button) == Qt.green
