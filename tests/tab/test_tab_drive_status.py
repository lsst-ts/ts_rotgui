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


@pytest.mark.asyncio
async def test_set_signal_drive(widget: TabDriveStatus) -> None:

    # Triggered
    widget.model.report_drive_status(
        [0xFFFF, 0xFFFF],
        [0xFFFF, 0xFFFF],
        [0xFFFFFFFF, 0xFFFFFFFF],
        [0xE0, 0xE0],
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for axis in ["axis_a", "axis_b"]:
        for idx, indicator in enumerate(widget._list_status_word[axis]):
            if idx == 3:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            elif idx in [6, 7, 8, 11]:
                assert indicator.palette().color(QPalette.Base) == Qt.yellow
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

        for indicator in widget._list_latching_fault_status[axis]:
            assert indicator.palette().color(QPalette.Base) == Qt.red

        for idx, indicator in enumerate(widget._list_copley_status[axis]):
            if idx in [0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 18, 22, 28, 29, 30]:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            elif idx in [7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25]:
                assert indicator.palette().color(QPalette.Base) == Qt.yellow
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

        for idx, indicator in enumerate(widget._list_input_pin_state[axis]):
            if idx in [1, 2]:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

    # Not triggered
    widget.model.report_drive_status([0, 0], [0, 0], [0, 0], [0, 0])

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for axis in ["axis_a", "axis_b"]:
        assert (
            widget._list_input_pin_state[axis][0].palette().color(QPalette.Base)
            == Qt.red
        )
