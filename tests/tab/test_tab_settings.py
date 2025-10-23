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
from lsst.ts.guitool import (
    LOG_LEVEL_MAXIMUM,
    LOG_LEVEL_MINIMUM,
    POINT_SIZE_MAXIMUM,
    POINT_SIZE_MINIMUM,
    PORT_MAXIMUM,
    PORT_MINIMUM,
    REFRESH_FREQUENCY_MAXIMUM,
    REFRESH_FREQUENCY_MINIMUM,
    TIMEOUT_MINIMUM,
)
from lsst.ts.rotgui import Model
from lsst.ts.rotgui.tab import TabSettings
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from qasync import QApplication


@pytest.fixture
def widget(qtbot: QtBot) -> TabSettings:
    widget = TabSettings("Settings", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabSettings) -> None:
    connection_information = widget.model.connection_information
    assert widget._settings["host"].text() == connection_information["host"]
    assert widget._settings["port"].value() == connection_information["port"]
    assert widget._settings["timeout_connection"].value() == connection_information["timeout_connection"]

    assert widget._settings["log_level"].value() == widget.model.log.level
    assert widget._settings["refresh_frequency"].value() == int(1000 / widget.model.duration_refresh)

    app = QApplication.instance()
    assert widget._settings["point_size"].value() == app.font().pointSize()

    assert widget._settings["port"].minimum() == PORT_MINIMUM
    assert widget._settings["port"].maximum() == PORT_MAXIMUM

    assert widget._settings["timeout_connection"].minimum() == TIMEOUT_MINIMUM

    assert widget._settings["log_level"].minimum() == LOG_LEVEL_MINIMUM
    assert widget._settings["log_level"].maximum() == LOG_LEVEL_MAXIMUM

    line_edit = widget._settings["host"]
    font_metrics = line_edit.fontMetrics()
    assert line_edit.minimumWidth() == font_metrics.boundingRect(line_edit.text()).width() + 20

    assert widget._settings["refresh_frequency"].minimum() == REFRESH_FREQUENCY_MINIMUM
    assert widget._settings["refresh_frequency"].maximum() == REFRESH_FREQUENCY_MAXIMUM

    assert widget._settings["point_size"].minimum() == POINT_SIZE_MINIMUM
    assert widget._settings["point_size"].maximum() == POINT_SIZE_MAXIMUM


@pytest.mark.asyncio
async def test_callback_apply_host(qtbot: QtBot, widget: TabSettings) -> None:
    widget._settings["host"].setText("newHost")
    widget._settings["port"].setValue(1)
    widget._settings["timeout_connection"].setValue(2)

    qtbot.mouseClick(widget._buttons["apply_host"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    connection_information = widget.model.connection_information
    assert connection_information["host"] == "newHost"
    assert connection_information["port"] == 1
    assert connection_information["timeout_connection"] == 2


@pytest.mark.asyncio
async def test_callback_apply_general(qtbot: QtBot, widget: TabSettings) -> None:
    widget._settings["log_level"].setValue(11)
    widget._settings["refresh_frequency"].setValue(5)
    widget._settings["point_size"].setValue(12)

    qtbot.mouseClick(widget._buttons["apply_general"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.model.log.level == 11
    assert widget.model.duration_refresh == 200

    app = QApplication.instance()
    assert app.font().pointSize() == 12
