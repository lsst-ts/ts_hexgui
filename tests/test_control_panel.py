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
from lsst.ts.hexgui import (
    CAM_UV_MAX_DEG,
    CAM_W_MAX_DEG,
    CAM_W_MIN_DEG,
    CAM_XY_MAX_MIC,
    CAM_Z_MAX_MIC,
    CAM_Z_MIN_MIC,
    MAX_ACCEL_LIMIT,
    MAX_ACTUATOR_RANGE_MIC,
    MAX_ANGULAR_VEL_LIMIT,
    MAX_LINEAR_VEL_LIMIT,
    MAX_PIVOT_X_MIC,
    MAX_PIVOT_Y_MIC,
    MAX_PIVOT_Z_MIC,
    NUM_STRUT,
    CommandSource,
    Config,
    ControlPanel,
    Model,
    MotionPattern,
)
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> ControlPanel:
    widget = ControlPanel(Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: ControlPanel) -> None:

    assert widget._command_parameters["position_x"].maximum() == CAM_XY_MAX_MIC
    assert widget._command_parameters["position_x"].minimum() == -CAM_XY_MAX_MIC

    assert widget._command_parameters["position_y"].maximum() == CAM_XY_MAX_MIC
    assert widget._command_parameters["position_y"].minimum() == -CAM_XY_MAX_MIC

    assert widget._command_parameters["position_z"].maximum() == CAM_Z_MAX_MIC
    assert widget._command_parameters["position_z"].minimum() == CAM_Z_MIN_MIC

    assert widget._command_parameters["position_rx"].maximum() == CAM_UV_MAX_DEG
    assert widget._command_parameters["position_rx"].minimum() == -CAM_UV_MAX_DEG

    assert widget._command_parameters["position_ry"].maximum() == CAM_UV_MAX_DEG
    assert widget._command_parameters["position_ry"].minimum() == -CAM_UV_MAX_DEG

    assert widget._command_parameters["position_rz"].maximum() == CAM_W_MAX_DEG
    assert widget._command_parameters["position_rz"].minimum() == CAM_W_MIN_DEG

    for idx in range(NUM_STRUT):
        assert (
            widget._command_parameters[f"strut_{idx}"].maximum()
            == MAX_ACTUATOR_RANGE_MIC
        )
        assert (
            widget._command_parameters[f"strut_{idx}"].minimum()
            == -MAX_ACTUATOR_RANGE_MIC
        )

    assert widget._command_parameters["pivot_x"].maximum() == MAX_PIVOT_X_MIC
    assert widget._command_parameters["pivot_x"].minimum() == -MAX_PIVOT_X_MIC

    assert widget._command_parameters["pivot_y"].maximum() == MAX_PIVOT_Y_MIC
    assert widget._command_parameters["pivot_y"].minimum() == -MAX_PIVOT_Y_MIC

    assert widget._command_parameters["pivot_z"].maximum() == MAX_PIVOT_Z_MIC
    assert widget._command_parameters["pivot_z"].minimum() == -MAX_PIVOT_Z_MIC

    assert (
        widget._command_parameters["linear_velocity_xy"].maximum()
        == MAX_LINEAR_VEL_LIMIT
    )
    assert (
        widget._command_parameters["linear_velocity_z"].maximum()
        == MAX_LINEAR_VEL_LIMIT
    )

    assert (
        widget._command_parameters["angular_velocity_rxry"].maximum()
        == MAX_ANGULAR_VEL_LIMIT
    )
    assert (
        widget._command_parameters["angular_velocity_rz"].maximum()
        == MAX_ANGULAR_VEL_LIMIT
    )

    assert widget._command_parameters["acceleration"].maximum() == MAX_ACCEL_LIMIT


@pytest.mark.asyncio
async def test_callback_command(qtbot: QtBot, widget: ControlPanel) -> None:

    # Single command parameter
    qtbot.mouseClick(widget._commands["enabled_substate"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["state"].isEnabled() is False
    assert widget._command_parameters["enabled_substate"].isEnabled() is True
    assert widget._command_parameters["position_x"].isEnabled() is False
    assert widget._command_parameters["position_y"].isEnabled() is False
    assert widget._command_parameters["position_z"].isEnabled() is False

    # Multiple command parameters
    qtbot.mouseClick(widget._commands["pivot"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["state"].isEnabled() is False
    assert widget._command_parameters["enabled_substate"].isEnabled() is False
    assert widget._command_parameters["pivot_x"].isEnabled() is True
    assert widget._command_parameters["pivot_y"].isEnabled() is True
    assert widget._command_parameters["pivot_z"].isEnabled() is True


@pytest.mark.asyncio
async def test_check_dangerous_commands(widget: ControlPanel) -> None:

    assert await widget._check_dangerous_commands() is False


def test_get_selected_command(widget: ControlPanel) -> None:

    for name, command in widget._commands.items():
        command.setChecked(True)

        assert widget._get_selected_command() == name


def test_get_motion_pattern(widget: ControlPanel) -> None:

    assert widget._get_motion_pattern() == MotionPattern.Sync

    widget._command_parameters["motion_pattern"].setCurrentIndex(1)
    assert widget._get_motion_pattern() == MotionPattern.Async


def test_update_fault_status(widget: ControlPanel) -> None:

    widget._update_fault_status(True)
    assert widget._indicators["fault"].text() == "Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.red

    widget._update_fault_status(False)
    assert widget._indicators["fault"].text() == "Not Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.green


@pytest.mark.asyncio
async def test_set_signal_state(widget: ControlPanel) -> None:

    command_source = CommandSource.CSC
    state = MTHexapod.ControllerState.FAULT
    enabled_substate = MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT

    widget.model.report_state(command_source, state, enabled_substate)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels["source"].text() == command_source.name
    assert widget._labels["state"].text() == state.name
    assert widget._labels["enabled_substate"].text() == enabled_substate.name

    assert widget._indicators["fault"].text() == "Faulted"
    assert widget._indicators["fault"].palette().color(QPalette.Button) == Qt.red


@pytest.mark.asyncio
async def test_set_signal_config(widget: ControlPanel) -> None:

    config = Config()
    for idx in range(3):
        config.pivot[idx] = float(idx + 1)
    config.drives_enabled = True

    widget.model.report_config(config)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["pivot_x"].value() == 1.0
    assert widget._command_parameters["pivot_y"].value() == 2.0
    assert widget._command_parameters["pivot_z"].value() == 3.0

    assert widget._indicators["drive"].text() == "On"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.green


def test_update_drive_status(widget: ControlPanel) -> None:

    widget._update_drive_status(True)
    assert widget._indicators["drive"].text() == "On"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.green

    widget._update_drive_status(False)
    assert widget._indicators["drive"].text() == "Off"
    assert widget._indicators["drive"].palette().color(QPalette.Button) == Qt.gray
