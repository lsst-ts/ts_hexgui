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
from lsst.ts.hexgui import CommandSource, ControlPanel, Model
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

    assert widget._command_parameters["position_x"].maximum() == 99.99
    assert widget._command_parameters["position_x"].minimum() == 0.0


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
    assert widget._command_parameters["position_x"].isEnabled() is True
    assert widget._command_parameters["position_y"].isEnabled() is True
    assert widget._command_parameters["position_z"].isEnabled() is True


def test_update_fault_status(widget: ControlPanel) -> None:

    widget._update_fault_status(True)
    assert widget._indicator_fault.text() == "Faulted"
    assert widget._indicator_fault.palette().color(QPalette.Button) == Qt.red

    widget._update_fault_status(False)
    assert widget._indicator_fault.text() == "Not Faulted"
    assert widget._indicator_fault.palette().color(QPalette.Button) == Qt.green


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

    assert widget._indicator_fault.text() == "Faulted"
    assert widget._indicator_fault.palette().color(QPalette.Button) == Qt.red
