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

import logging

import pytest
from lsst.ts.rotgui import Model
from lsst.ts.rotgui.tab import TabDriveStatus
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabDriveStatus:
    widget = TabDriveStatus("Drive Status (Axis A+B)", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabDriveStatus) -> None:

    assert len(widget._list_status_word["axis_a"]) == 16
    assert len(widget._list_latching_fault_status["axis_a"]) == 16
    assert len(widget._list_copley_status["axis_a"]) == 32
    assert len(widget._list_input_pin_state["axis_a"]) == 3

    assert len(widget._list_simulink_flag) == 11


def test_update_boolean_indicator_color(widget: TabDriveStatus) -> None:

    indicator = widget._list_simulink_flag[0]

    # On
    widget._update_boolean_indicator_color(indicator, Qt.green, Qt.red, True)

    assert indicator.palette().color(QPalette.Base) == Qt.green

    # Off
    widget._update_boolean_indicator_color(indicator, Qt.green, Qt.red, False)

    assert indicator.palette().color(QPalette.Base) == Qt.red
