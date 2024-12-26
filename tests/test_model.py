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

import logging

import pytest
from lsst.ts.hexgui import (
    NUM_DEGREE_OF_FREEDOM,
    NUM_DRIVE,
    NUM_STRUT,
    CommandSource,
    Config,
    Model,
)
from lsst.ts.xml.enums import MTHexapod
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD)


def test_init(model: Model) -> None:
    assert len(model.signals) == 7


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
        model.report_position(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_DEGREE_OF_FREEDOM, False
        )


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

    assert (
        model._status.substate_enabled
        == MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT.value
    )


def test_report_application_status(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["application_status"].status, timeout=TIMEOUT):
        model.report_application_status(1)

    assert model._status.application_status == 1


def test_report_drive_status(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["drive"].status_word, timeout=TIMEOUT):
        model.report_drive_status(
            [1] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT
        )

    assert model._status.status_word == [1] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].latching_fault, timeout=TIMEOUT):
        model.report_drive_status(
            [1] * NUM_STRUT, [2] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT
        )

    assert model._status.latching_fault == [2] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].copley_status, timeout=TIMEOUT):
        model.report_drive_status(
            [1] * NUM_STRUT, [2] * NUM_STRUT, [3] * NUM_STRUT, [0] * NUM_STRUT
        )

    assert model._status.copley_status == [3] * NUM_STRUT

    with qtbot.waitSignal(model.signals["drive"].input_pin, timeout=TIMEOUT):
        model.report_drive_status(
            [1] * NUM_STRUT, [2] * NUM_STRUT, [3] * NUM_STRUT, [4] * NUM_STRUT
        )

    assert model._status.input_pin == [4] * NUM_STRUT
