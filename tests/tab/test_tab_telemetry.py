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
from lsst.ts.hexgui import Model
from lsst.ts.hexgui.tab import TabTelemetry
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabTelemetry:
    widget = TabTelemetry("Telemetry", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabTelemetry) -> None:
    assert len(widget._application_status) == 15


@pytest.mark.asyncio
async def test_set_signal_application_status(widget: TabTelemetry) -> None:
    widget.model.report_application_status(0xFFFF)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx, indicator in enumerate(widget._application_status):
        if idx in [0, 5, 6, 7, 8, 9, 11, 13, 14]:
            assert indicator.palette().color(QPalette.Base) == Qt.red
        else:
            assert indicator.palette().color(QPalette.Base) == Qt.green


@pytest.mark.asyncio
async def test_set_signal_control(widget: TabTelemetry) -> None:
    widget.model.report_control_data(
        [1.1, 2.2, 3.3, 4.4, 5.5, 6.6],
        [7.7, 8.8, 9.9, 10.0, 11.1, 12.2],
        13.3,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._telemetry_strut["command_acceleration_0"].text() == "1.100 um/sec^2"
    assert widget._telemetry_strut["command_acceleration_1"].text() == "2.200 um/sec^2"
    assert widget._telemetry_strut["command_acceleration_2"].text() == "3.300 um/sec^2"
    assert widget._telemetry_strut["command_acceleration_3"].text() == "4.400 um/sec^2"
    assert widget._telemetry_strut["command_acceleration_4"].text() == "5.500 um/sec^2"
    assert widget._telemetry_strut["command_acceleration_5"].text() == "6.600 um/sec^2"

    assert widget._telemetry_strut["command_position_0"].text() == "7.700 um"
    assert widget._telemetry_strut["command_position_1"].text() == "8.800 um"
    assert widget._telemetry_strut["command_position_2"].text() == "9.900 um"
    assert widget._telemetry_strut["command_position_3"].text() == "10.000 um"
    assert widget._telemetry_strut["command_position_4"].text() == "11.100 um"
    assert widget._telemetry_strut["command_position_5"].text() == "12.200 um"

    assert widget._telemetry_position["time_frame_difference"].text() == "13.3000000 sec"


@pytest.mark.asyncio
async def test_set_signal_position(widget: TabTelemetry) -> None:
    widget.model.report_position(
        [1.1, 2.2, 3.3, 4.4, 5.5, 6.6],
        [7.7, 8.8, 9.9, 10.0, 11.1, 12.2],
        [13.3, 14.4, 15.5, 16.6, 17.7, 18.8],
        True,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._telemetry_strut["position_0"].text() == "1.100 um"
    assert widget._telemetry_strut["position_1"].text() == "2.200 um"
    assert widget._telemetry_strut["position_2"].text() == "3.300 um"
    assert widget._telemetry_strut["position_3"].text() == "4.400 um"
    assert widget._telemetry_strut["position_4"].text() == "5.500 um"
    assert widget._telemetry_strut["position_5"].text() == "6.600 um"

    assert widget._telemetry_strut["position_error_0"].text() == "7.700 um"
    assert widget._telemetry_strut["position_error_1"].text() == "8.800 um"
    assert widget._telemetry_strut["position_error_2"].text() == "9.900 um"
    assert widget._telemetry_strut["position_error_3"].text() == "10.000 um"
    assert widget._telemetry_strut["position_error_4"].text() == "11.100 um"
    assert widget._telemetry_strut["position_error_5"].text() == "12.200 um"

    assert widget._telemetry_position["position_x"].text() == "13.300 um"
    assert widget._telemetry_position["position_y"].text() == "14.400 um"
    assert widget._telemetry_position["position_z"].text() == "15.500 um"
    assert widget._telemetry_position["position_rx"].text() == "16.6000000 deg"
    assert widget._telemetry_position["position_ry"].text() == "17.7000000 deg"
    assert widget._telemetry_position["position_rz"].text() == "18.8000000 deg"

    assert widget._telemetry_position["in_motion"].text() == "<font color='green'>True</font>"


@pytest.mark.asyncio
async def test_set_signal_power(widget: TabTelemetry) -> None:
    widget.model.report_power([1.1, 2.2, 3.3, 4.4, 5.5, 6.6], [7.7, 8.8, 9.9])

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._telemetry_strut["current_0"].text() == "1.100000 A"
    assert widget._telemetry_strut["current_1"].text() == "2.200000 A"
    assert widget._telemetry_strut["current_2"].text() == "3.300000 A"
    assert widget._telemetry_strut["current_3"].text() == "4.400000 A"
    assert widget._telemetry_strut["current_4"].text() == "5.500000 A"
    assert widget._telemetry_strut["current_5"].text() == "6.600000 A"
