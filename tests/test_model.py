# This file is part of ts_hexgui.
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
from pytestqt.qtbot import QtBot

from lsst.ts import salobj
from lsst.ts.hexgui import (
    CAM_UV_MAX_DEG,
    CAM_W_MAX_DEG,
    CAM_W_MIN_DEG,
    CAM_XY_MAX_MIC,
    CAM_Z_MAX_MIC,
    CAM_Z_MIN_MIC,
    NUM_DEGREE_OF_FREEDOM,
    NUM_DRIVE,
    NUM_STRUT,
    CommandCode,
    CommandSource,
    Config,
    Model,
    MotionPattern,
    TriggerEnabledSubState,
    TriggerState,
)
from lsst.ts.xml.enums import MTHexapod

TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD)


@pytest_asyncio.fixture
async def model_async() -> Model:
    async with Model(
        logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD, is_simulation_mode=True
    ) as model_sim:
        await model_sim.connect()

        yield model_sim


@pytest.mark.asyncio
async def test_init(model_async: Model) -> None:
    assert len(model_async.signals) == 7

    assert tuple(model_async._mock_ctrl.config.pos_limits) == (
        CAM_XY_MAX_MIC,
        CAM_Z_MIN_MIC,
        CAM_Z_MAX_MIC,
        CAM_UV_MAX_DEG,
        CAM_W_MIN_DEG,
        CAM_W_MAX_DEG,
    )
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


def test_is_in_motion(model: Model) -> None:
    status_words = [0] * NUM_STRUT
    assert model._is_in_motion(status_words) is False

    status_words[0] = 0x4000
    assert model._is_in_motion(status_words) is True


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
    values = [1.0, 3.0]
    patterns = [MotionPattern.Async, MotionPattern.Sync]
    for trigger_state, value, pattern in zip(TriggerEnabledSubState, values, patterns):
        command = model.make_command_enabled_substate(trigger_state, pattern)

        assert command.COMMANDER == 1
        assert command.code == CommandCode.SET_ENABLED_SUBSTATE.value
        assert command.param1 == value
        assert command.param2 == float(pattern.value)


def test_report_default(qtbot: QtBot, model: Model) -> None:
    signals = [
        model.signals["state"].command_source,
        model.signals["state"].state,
        model.signals["state"].substate_enabled,
        model.signals["drive"].status_word,
        model.signals["drive"].latching_fault,
        model.signals["drive"].copley_status,
        model.signals["drive"].input_pin,
        model.signals["application_status"].status,
        model.signals["config"].config,
        model.signals["control"].command_acceleration,
        model.signals["control"].command_position,
        model.signals["control"].time_difference,
        model.signals["position"].strut_position,
        model.signals["position"].strut_position_error,
        model.signals["position"].hexapod_position,
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
        model.signals["control"].command_acceleration,
        model.signals["control"].command_position,
        model.signals["control"].time_difference,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_control_data([0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0)


def test_report_position(qtbot: QtBot, model: Model) -> None:
    signals = [
        model.signals["position"].strut_position,
        model.signals["position"].strut_position_error,
        model.signals["position"].hexapod_position,
        model.signals["position"].in_motion,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_position([0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_DEGREE_OF_FREEDOM, False)


def test_report_power(qtbot: QtBot, model: Model) -> None:
    signals = [
        model.signals["power"].current,
        model.signals["power"].voltage,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_power([0.0] * NUM_STRUT, [0.0] * NUM_DRIVE)


def test_report_state(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signals["state"].command_source, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTHexapod.ControllerState.STANDBY,
            MTHexapod.EnabledSubstate.STATIONARY,
        )

    assert model._status.command_source == CommandSource.CSC.value

    with qtbot.waitSignal(model.signals["state"].state, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTHexapod.ControllerState.ENABLED,
            MTHexapod.EnabledSubstate.STATIONARY,
        )

    assert model._status.state == MTHexapod.ControllerState.ENABLED.value

    with qtbot.waitSignal(model.signals["state"].substate_enabled, timeout=TIMEOUT):
        model.report_state(
            CommandSource.CSC,
            MTHexapod.ControllerState.ENABLED,
            MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT,
        )

    assert model._status.substate_enabled == MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT.value


def test_report_application_status(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signals["application_status"].status, timeout=TIMEOUT):
        model.report_application_status(1)

    assert model._status.application_status == 1


def test_report_drive_status(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signals["drive"].status_word, timeout=TIMEOUT):
        model.report_drive_status([1] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT)

    assert model._status.status_word == [1] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].latching_fault, timeout=TIMEOUT):
        model.report_drive_status([1] * NUM_STRUT, [2] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT)

    assert model._status.latching_fault == [2] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].copley_status, timeout=TIMEOUT):
        model.report_drive_status([1] * NUM_STRUT, [2] * NUM_STRUT, [3] * NUM_STRUT, [0] * NUM_STRUT)

    assert model._status.copley_status == [3] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].input_pin, timeout=TIMEOUT):
        model.report_drive_status([1] * NUM_STRUT, [2] * NUM_STRUT, [3] * NUM_STRUT, [4] * NUM_STRUT)

    assert model._status.input_pin == [4] * NUM_STRUT


@pytest.mark.asyncio
async def test_command_move_point_to_point(model_async: Model) -> None:
    await _enable_controller(model_async)
    await _move_point_to_point(
        model_async,
        param1=100.0,
        param2=200.0,
        param3=300.0,
        param4=0.1,
        param5=-0.1,
        param6=0.005,
    )

    await asyncio.sleep(1.0)

    assert tuple(model_async._mock_ctrl.telemetry.measured_xyz) == pytest.approx((100.0, 200.0, 300.0))
    assert tuple(model_async._mock_ctrl.telemetry.measured_uvw) == pytest.approx((0.1, -0.1, 0.005))


@pytest.mark.asyncio
async def _enable_controller(model_async: Model) -> None:
    command = model_async.make_command_state(TriggerState.Enable)
    await model_async.client.run_command(command)
    await asyncio.sleep(1.0)


@pytest.mark.asyncio
async def _move_point_to_point(
    model_async: Model,
    param1: float = 0.0,
    param2: float = 0.0,
    param3: float = 0.0,
    param4: float = 0.0,
    param5: float = 0.0,
    param6: float = 0.0,
) -> None:
    command_position_set = model_async.make_command(
        CommandCode.POSITION_SET,
        param1=param1,
        param2=param2,
        param3=param3,
        param4=param4,
        param5=param5,
        param6=param6,
    )
    await model_async.client.run_command(command_position_set)

    command_move = model_async.make_command_enabled_substate(
        TriggerEnabledSubState.Move,
        MotionPattern.Sync,
    )
    await model_async.client.run_command(command_move)


@pytest.mark.asyncio
async def test_command_stop(model_async: Model) -> None:
    await _enable_controller(model_async)
    await _move_point_to_point(model_async, param3=12000.0)

    await asyncio.sleep(0.5)

    assert model_async._status.substate_enabled == MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT.value

    command_stop = model_async.make_command_enabled_substate(
        TriggerEnabledSubState.Stop,
        MotionPattern.Sync,
    )
    await model_async.client.run_command(command_stop)

    await asyncio.sleep(1.0)

    assert model_async._status.substate_enabled == MTHexapod.EnabledSubstate.STATIONARY.value
    assert 0 < model_async._mock_ctrl.telemetry.measured_xyz[2] < 10000.0


@pytest.mark.asyncio
async def test_command_position_set(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(
        CommandCode.POSITION_SET,
        param1=100.0,
        param2=200.0,
        param3=300.0,
        param4=0.1,
        param5=-0.1,
        param6=0.005,
    )
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl._commanded_position == [
        100.0,
        200.0,
        300.0,
        0.1,
        -0.1,
        0.005,
    ]


@pytest.mark.asyncio
async def test_command_position_offset(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(
        CommandCode.POSITION_OFFSET,
        param1=100.0,
        param2=200.0,
        param3=300.0,
        param4=0.1,
        param5=-0.1,
        param6=0.005,
    )
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl._commanded_position == [
        100.0,
        200.0,
        300.0,
        0.1,
        -0.1,
        0.005,
    ]


@pytest.mark.asyncio
async def test_command_set_raw_strut(model_async: Model) -> None:
    command = model_async.make_command(CommandCode.SET_RAW_STRUT)
    with pytest.raises(salobj.ExpectedError):
        await model_async.client.run_command(command)


@pytest.mark.asyncio
async def test_command_set_pivot_point(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(CommandCode.SET_PIVOT_POINT, param1=1.0, param2=2.0, param3=3.0)
    await model_async.client.run_command(command)

    assert tuple(model_async._mock_ctrl.config.pivot) == (1.0, 2.0, 3.0)


@pytest.mark.asyncio
async def test_command_mask_limit_switch(model_async: Model) -> None:
    command = model_async.make_command(CommandCode.MASK_LIMIT_SW)
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
    command = model_async.make_command(CommandCode.CONFIG_ACCEL, param1=1.0)
    await model_async.client.run_command(command)

    assert model_async._mock_ctrl.config.acceleration_strut == 1.0

    # Out of range
    command_out = model_async.make_command(CommandCode.CONFIG_ACCEL, param1=1000.0)
    with pytest.raises(salobj.ExpectedError):
        await model_async.client.run_command(command_out)


@pytest.mark.asyncio
async def test_command_config_vel(model_async: Model) -> None:
    await _enable_controller(model_async)

    command = model_async.make_command(
        CommandCode.CONFIG_VEL, param1=0.01, param2=0.02, param3=0.03, param4=0.04
    )
    await model_async.client.run_command(command)

    assert tuple(model_async._mock_ctrl.config.vel_limits) == (0.01, 0.03, 0.02, 0.04)
