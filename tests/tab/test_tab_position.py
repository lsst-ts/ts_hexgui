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
from lsst.ts.hexgui import NUM_DEGREE_OF_FREEDOM, NUM_STRUT, Model
from lsst.ts.hexgui.tab import TabPosition
from lsst.ts.xml.enums import MTHexapod
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabPosition:
    widget = TabPosition(
        "Position", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD)
    )
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabPosition) -> None:

    widget._strut_lengths = list(range(1, NUM_STRUT + 1))
    widget._positions = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]

    await widget._callback_time_out()

    for idx, strut_length in enumerate(widget._strut_lengths):
        assert widget._figures["length"].get_points(idx)[-1].y() == strut_length

    for idx, position in enumerate(widget._positions):
        if idx < 3:
            assert widget._figures["displacement"].get_points(idx)[-1].y() == position
        else:
            assert widget._figures["angle"].get_points(idx - 3)[-1].y() == position


@pytest.mark.asyncio
async def test_set_signal_position_velocity(widget: TabPosition) -> None:

    widget.model.report_position(
        [10.1] * NUM_STRUT, [20.2] * NUM_STRUT, [30.3] * NUM_DEGREE_OF_FREEDOM, True
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._strut_lengths == [10.1] * NUM_STRUT
    assert widget._positions == [30.3] * NUM_DEGREE_OF_FREEDOM
