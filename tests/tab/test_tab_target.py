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

import logging

import pytest
from lsst.ts.rotgui import Model
from lsst.ts.rotgui.tab import TabTarget
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabTarget:
    widget = TabTarget("Target", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_add_target(widget: TabTarget) -> None:
    # Bad velocity and duration
    await widget._callback_add_target(is_prompted=False)

    assert widget._table_target.rowCount() == 0

    # Bad velocity
    widget._target_parameters["duration"].setValue(1.0)
    await widget._callback_add_target(is_prompted=False)

    assert widget._table_target.rowCount() == 0

    # Good velocity and duration
    widget._target_parameters["velocity"].setValue(1.0)
    await widget._callback_add_target(is_prompted=False)

    assert widget._table_target.rowCount() == 1


@pytest.mark.asyncio
async def test_callback_remove_target(widget: TabTarget) -> None:
    await _add_targets(widget)
    assert widget._table_target.rowCount() == 10

    # No selection
    await widget._callback_remove_target()

    assert widget._table_target.rowCount() == 10

    # Select the first to remove
    widget._table_target.selectRow(0)
    await widget._callback_remove_target()

    assert widget._table_target.rowCount() == 9
    assert widget._table_target.item(0, 0).text() == "1.0"

    # Select all to remove
    widget._table_target.selectAll()
    await widget._callback_remove_target()

    assert widget._table_target.rowCount() == 0


@pytest.mark.asyncio
async def _add_targets(widget: TabTarget) -> None:
    widget._target_parameters["velocity"].setValue(0.01)
    widget._target_parameters["duration"].setValue(15.0)

    for idx in range(10):
        widget._target_parameters["position"].setValue(idx)
        await widget._callback_add_target(is_prompted=False)


@pytest.mark.asyncio
async def test_callback_clear_targets(widget: TabTarget) -> None:
    await _add_targets(widget)
    assert widget._table_target.rowCount() == 10

    await widget._callback_clear_targets()

    assert widget._table_target.rowCount() == 0


@pytest.mark.asyncio
async def test_get_targets(widget: TabTarget) -> None:
    await _add_targets(widget)
    targets = widget.get_targets()

    assert len(targets) == 10
    assert targets[0] == [0.0, 0.01, 15.0]
    assert targets[9] == [9.0, 0.01, 15.0]
