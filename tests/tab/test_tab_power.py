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
from lsst.ts.rotgui.tab import TabPower
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabPower:
    widget = TabPower("Power", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabPower) -> None:

    widget._currents = [1.0, 2.0]
    widget._voltage = 3.0

    await widget._callback_time_out()

    assert widget._figures["current"].get_points(0)[-1].y() == 1.0
    assert widget._figures["current"].get_points(1)[-1].y() == 2.0

    assert widget._figures["voltage"].get_points(0)[-1].y() == 3.0


@pytest.mark.asyncio
async def test_set_signal_power(widget: TabPower) -> None:

    widget.model.report_power([10.1, 20.2], 30.3)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._currents == [10.1, 20.2]
    assert widget._voltage == 30.3
