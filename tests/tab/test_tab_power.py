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
from pytestqt.qtbot import QtBot

from lsst.ts.hexgui import NUM_DRIVE, NUM_STRUT, Model
from lsst.ts.hexgui.tab import TabPower
from lsst.ts.xml.enums import MTHexapod


@pytest.fixture
def widget(qtbot: QtBot) -> TabPower:
    widget = TabPower("Power", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabPower) -> None:
    widget._currents = list(range(1, NUM_STRUT + 1))
    widget._voltages = list(range(10, NUM_DRIVE + 10))

    await widget._callback_time_out()

    for idx in range(NUM_STRUT):
        assert widget._figures["current"].get_points(idx)[-1].y() == widget._currents[idx]

    for idx in range(NUM_DRIVE):
        assert widget._figures["voltage"].get_points(idx)[-1].y() == widget._voltages[idx]


@pytest.mark.asyncio
async def test_set_signal_power(widget: TabPower) -> None:
    widget.model.report_power([10.1, 20.2, 30.3, 40.4, 50.5, 60.6], [70.7, 80.8, 90.9])

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._currents == [10.1, 20.2, 30.3, 40.4, 50.5, 60.6]
    assert widget._voltages == [70.7, 80.8, 90.9]
