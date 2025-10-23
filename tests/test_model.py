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
import pytest_asyncio
from lsst.ts import salobj
from lsst.ts.rotgui import (
    NUM_STRUT,
    CommandCode,
    CommandSource,
    Config,
    Model,
    Telemetry,
    TriggerEnabledSubState,
    TriggerState,
)
from lsst.ts.xml.enums import MTRotator
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger())


@pytest_asyncio.fixture
async def model_async() -> Model:
    async with Model(logging.getLogger(), is_simulation_mode=True) as model_sim:
        await model_sim.connect()

        yield model_sim


@pytest.mark.asyncio
async def test_init(model_async: Model) -> None:
    assert len(model_async.signals) == 7

    assert model_async._mock_ctrl._commanded_position is None


@pytest.mark.asyncio
async def test_connect(model_async: Model) -> None:
    assert model_async.is_connected() is True


def test_is_connected(model: Model) -> None:
    assert model.is_connected() is False


@pytest.mark.asyncio
async def test_disconnect(model_async: Model) -> None:
    await model_async.disconnect()

    assert model_async.is_connected() is False


@pytest.mark.asyncio
async def test_command_move_point_to_point(model_async: Model) -> None:
    await _enable_controller(model_async)
    await _move_point_to_point(model_async, position=10.0)

    await asyncio.sleep(1.0)

    assert model_async._mock_ctrl.telemetry.current_pos == 10.0


@pytest.mark.asyncio
async def _enable_controller(model_async: Model) -> None:
    command = model_async.make_command_state(TriggerState.Enable)
    await model_async.client.run_command(command)
    await asyncio.sleep(1.0)


@pytest.mark.asyncio
async def _move_point_to_point(model_async: Model, position: float = 0.0) -> None:
    command_position_set = model_async.make_command(
        CommandCode.POSITION_SET,
        param1=position,
    )
    await model_async.client.run_command(command_position_set)

    command_move = model_async.make_command_enabled_substate(
        TriggerEnabledSubState.Move,
    )
    await model_async.client.run_command(command_move)


@pytest.mark.asyncio
async def test_command_stop(model_async: Model) -> None:
    await _enable_controller(model_async)
    await _move_point_to_point(model_async, position=90.0)

    await asyncio.sleep(0.5)

    assert model_async._status.substate_enabled == MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT.value

    command_stop = model_async.make_command_enabled_substate(
        TriggerEnabledSubState.Stop,
    )
    await model_async.client.run_command(command_stop)

    await asyncio.sleep(1.0)

    assert model_async._status.substate_enabled == MTRotator.EnabledSubstate.STATIONARY.value
    assert 0.0 < model_async._mock_ctrl.telemetry.current_pos < 90.0


@pytest.mark.asyncio
async def test_command_position_set(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(
        CommandCode.POSITION_SET,
        param1=80.0,
    )
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl._commanded_position == 80.0


@pytest.mark.asyncio
async def test_command_set_constant_vel(model_async: Model) -> None:
    command = model_async.make_command(CommandCode.SET_CONSTANT_VEL)
    with pytest.raises(salobj.ExpectedError):
        await model_async.client.run_command(command)


@pytest.mark.asyncio
async def test_command_switch_command_source(model_async: Model) -> None:
    command = model_async.make_command(CommandCode.CMD_SOURCE, param1=1.0)
    await model_async.client.run_command(command)

    await asyncio.sleep(1.0)

    assert model_async._mock_ctrl._is_csc_commander is True
    assert model_async._status.command_source == CommandSource.CSC.value


@pytest.mark.asyncio
async def test_command_config_accel(model_async: Model) -> None:
    await _enable_controller(model_async)

    # In range
    command = model_async.make_command(CommandCode.CONFIG_ACCEL, param1=0.8)
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl.config.accel_limit == 0.8

    # Out of range
    command_out = model_async.make_command(CommandCode.CONFIG_ACCEL, param1=1.1)
    with pytest.raises(salobj.ExpectedError):
        await model_async.client.run_command(command_out)


@pytest.mark.asyncio
async def test_command_config_vel(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(CommandCode.CONFIG_VEL, param1=0.3)
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl.config.velocity_limit == 0.3


@pytest.mark.asyncio
async def test_command_config_accel_emergency(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(CommandCode.CONFIG_ACCEL_EMERGENCY, param1=0.5)
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl.config.emergency_accel_limit == 0.5


@pytest.mark.asyncio
async def test_command_config_jerk_emergency(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(CommandCode.CONFIG_JERK_EMERGENCY, param1=0.4)
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl.config.emergency_jerk_limit == 0.4


def test_get_simulink_flag(model: Model) -> None:
    telemetry = Telemetry()
    telemetry.flags_new_pt2pt_command = 1.0
    telemetry.flags_no_new_track_cmd_error = 1.0

    assert model._get_simulink_flag(telemetry) == 1032


def test_is_csc_commander(model: Model) -> None:
    assert model.is_csc_commander() is False

    model._status.command_source = CommandSource.CSC.value
    assert model.is_csc_commander() is True


def test_assert_is_connected(model: Model) -> None:
    with pytest.raises(RuntimeError):
        model.assert_is_connected()


def test_make_command(model: Model) -> None:
    command_code = CommandCode.ENABLE_DRIVES
    command = model.make_command(
        command_code,
        param1=1.0,
        param2=2.0,
        param3=3.0,
        param4=4.0,
        param5=5.0,
        param6=6.0,
    )

    assert command.COMMANDER == 1
    assert command.code == command_code.value
    assert command.param1 == 1.0
    assert command.param2 == 2.0
    assert command.param3 == 3.0
    assert command.param4 == 4.0
    assert command.param5 == 5.0
    assert command.param6 == 6.0


def test_make_command_state(model: Model) -> None:
    values = [2.0, 3.0, 6.0]
    for trigger_state, value in zip(TriggerState, values):
        command = model.make_command_state(trigger_state)

        assert command.COMMANDER == 1
        assert command.code == CommandCode.SET_STATE.value
        assert command.param1 == value


def test_make_command_enabled_substate(model: Model) -> None:
    values = [1.0, 3.0, 6.0]
    for trigger_state, value in zip(TriggerEnabledSubState, values):
        command = model.make_command_enabled_substate(trigger_state)

        assert command.COMMANDER == 1
        assert command.code == CommandCode.SET_ENABLED_SUBSTATE.value
        assert command.param1 == value


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
        model.signals["power"].current,
        model.signals["power"].voltage,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_default()


def test_compare_status_and_report_exception(model: Model) -> None:
    with pytest.raises(TypeError):
        model._compare_status_and_report("command_source", [1, 2], model.signals["state"].command_source)


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
        model.report_control_data([0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0)


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

    assert model._status.substate_enabled == MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT.value

    with qtbot.waitSignal(model.signals["state"].substate_fault, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTRotator.ControllerState.ENABLED,
            MTRotator.EnabledSubstate.MOVING_POINT_TO_POINT,
            MTRotator.FaultSubstate.EMERGENCY_STOPPING,
        )

    assert model._status.substate_fault == MTRotator.FaultSubstate.EMERGENCY_STOPPING.value


def test_report_application_status(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signals["application_status"].status, timeout=TIMEOUT):
        model.report_application_status(1, 0)

    assert model._status.application_status == 1

    with qtbot.waitSignal(model.signals["application_status"].simulink_flag, timeout=TIMEOUT):
        model.report_application_status(1, 2)

    assert model._status.simulink_flag == 2


def test_report_drive_status(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signals["drive"].status_word, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [0] * NUM_STRUT, [0] * NUM_STRUT, 0)

    assert model._status.status_word == [1, 2]

    with qtbot.waitSignal(model.signals["drive"].latching_fault, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [0] * NUM_STRUT, 0)

    assert model._status.latching_fault == [3, 4]

    with qtbot.waitSignal(model.signals["drive"].copley_status, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [5, 6], 0)

    assert model._status.copley_status == [5, 6]

    with qtbot.waitSignal(model.signals["drive"].input_pin, timeout=TIMEOUT):
        model.report_drive_status([1, 2], [3, 4], [5, 6], 7)

    assert model._status.input_pin == 7
