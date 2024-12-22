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
from lsst.ts.rotgui import NUM_STRUT, CommandSource, Config, Model
from lsst.ts.xml.enums import MTRotator
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger())


def test_init(model: Model) -> None:
    assert len(model.signals) == 7


def test_report_default(qtbot: QtBot, model: Model) -> None:

    signals = [
        model.signals["state"].command_source,
        model.signals["state"].state,
        model.signals["state"].substate_enabled,
        model.signals["state"].substate_fault,
        model.signals["drive"].status_word,
        model.signals["drive"].latching_fault,
        model.signals["drive"].copley_status,
        model.signals["drive"].input_pin,
        model.signals["application_status"].status,
        model.signals["application_status"].simulink_flag,
        model.signals["config"].config,
        model.signals["control"].rate_command,
        model.signals["control"].rate_feedback,
        model.signals["control"].torque,
        model.signals["control"].time_difference,
        model.signals["position_velocity"].position_current,
        model.signals["position_velocity"].position_command,
        model.signals["position_velocity"].odometer,
        model.signals["position_velocity"].velocity,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_default()


def test_compare_status_and_report_exception(model: Model) -> None:

    with pytest.raises(TypeError):
        model._compare_status_and_report(
            "command_source", [1, 2], model.signals["state"].command_source
        )


def test_report_config(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["config"].config, timeout=TIMEOUT):
        model.report_config(Config())


def test_report_control_data(qtbot: QtBot, model: Model) -> None:

    signals = [
        model.signals["control"].rate_command,
        model.signals["control"].rate_feedback,
        model.signals["control"].torque,
        model.signals["control"].time_difference,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_control_data(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0
        )


def test_report_position_velocity(qtbot: QtBot, model: Model) -> None:

    signals = [
        model.signals["position_velocity"].position_current,
        model.signals["position_velocity"].position_command,
        model.signals["position_velocity"].odometer,
        model.signals["position_velocity"].velocity,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_position_velocity(0.0, 0.0, 0.0, 0.0)


def test_report_power(qtbot: QtBot, model: Model) -> None:

    signals = [
        model.signals["power"].current,
        model.signals["power"].voltage,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_power([0.0] * NUM_STRUT, 0.0)


def test_report_state(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].command_source, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTRotator.ControllerState.STANDBY,
            MTRotator.EnabledSubstate.STATIONARY,
            MTRotator.FaultSubstate.NO_ERROR,
        )

    assert model._status.command_source == CommandSource.CSC.value

    with qtbot.waitSignal(model.signals["state"].state, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTRotator.ControllerState.ENABLED,
            MTRotator.EnabledSubstate.STATIONARY,
            MTRotator.FaultSubstate.NO_ERROR,
        )

    assert model._status.state == MTRotator.ControllerState.ENABLED.value

    with qtbot.waitSignal(model.signals["state"].substate_enabled, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTRotator.ControllerState.ENABLED,
            MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT,
            MTRotator.FaultSubstate.NO_ERROR,
        )

    assert (
        model._status.substate_enabled
        == MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT.value
    )

    with qtbot.waitSignal(model.signals["state"].substate_fault, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTRotator.ControllerState.ENABLED,
            MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT,
            MTRotator.FaultSubstate.EMERGENCY_STOPPING,
        )

    assert (
        model._status.substate_fault == MTRotator.FaultSubstate.EMERGENCY_STOPPING.value
    )


def test_report_application_status(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["application_status"].status, timeout=TIMEOUT):
        model.report_application_status(1, 0)

    assert model._status.application_status == 1

    with qtbot.waitSignal(
        model.signals["application_status"].simulink_flag, timeout=TIMEOUT
    ):
        model.report_application_status(1, 2)

    assert model._status.simulink_flag == 2


def test_report_drive_status(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["drive"].status_word, timeout=TIMEOUT):
        model.report_drive_status(
            [1, 2], [0] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT
        )

    assert model._status.status_word == [1, 2]

    with qtbot.waitSignal(model.signals["drive"].latching_fault, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [0] * NUM_STRUT, [0] * NUM_STRUT)

    assert model._status.latching_fault == [3, 4]

    with qtbot.waitSignal(model.signals["drive"].copley_status, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [5, 6], [0] * NUM_STRUT)

    assert model._status.copley_status == [5, 6]

    with qtbot.waitSignal(model.signals["drive"].input_pin, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [5, 6], [7, 8])

    assert model._status.input_pin == [7, 8]
