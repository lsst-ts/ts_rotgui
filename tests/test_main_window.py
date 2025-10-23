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

import pytest
from lsst.ts.guitool import get_config_dir, read_yaml_file
from lsst.ts.rotgui import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> MainWindow:
    widget = MainWindow(False, False, False, log_level=13)
    qtbot.addWidget(widget)

    return widget


def test_init(widget: MainWindow) -> None:
    assert widget.log.level == 13

    tool_bar = widget.findChildren(QToolBar)[0]
    actions = tool_bar.actions()

    assert len(actions) == 4

    connection_information = widget.model.connection_information
    configuration = _get_config()
    assert connection_information["host"] == configuration["host"]
    assert connection_information["port"] == configuration["port"]
    assert connection_information["timeout_connection"] == configuration["connection_timeout"]


def _get_config() -> dict:
    filepath = get_config_dir("MTRotator/v2") / "default_gui.yaml"
    return read_yaml_file(filepath)


def test_get_action(widget: MainWindow) -> None:
    button_exit = widget._get_action("Exit")
    assert button_exit.text() == "Exit"

    button_wrong_action = widget._get_action("WrongAction")
    assert button_wrong_action is None


@pytest.mark.asyncio
async def test_callback_settings(qtbot: QtBot, widget: MainWindow) -> None:
    assert widget._tab_settings.isVisible() is False

    button_settings = widget._get_action("Settings")
    qtbot.mouseClick(button_settings, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_settings.isVisible() is True
