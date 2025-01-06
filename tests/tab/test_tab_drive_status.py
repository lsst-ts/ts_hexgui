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
from lsst.ts.hexgui import NUM_STRUT, Model
from lsst.ts.hexgui.tab import TabDriveStatus
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabDriveStatus:
    widget = TabDriveStatus(
        "Drive Status", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD)
    )
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabDriveStatus) -> None:

    assert len(widget._list_status_word["strut_0"]) == 16
    assert len(widget._list_latching_fault_status["strut_0"]) == 16
    assert len(widget._list_copley_status["strut_0"]) == 32
    assert len(widget._list_input_pin_state["strut_0"]) == 3


@pytest.mark.asyncio
async def test_set_signal_drive(widget: TabDriveStatus) -> None:

    # Triggered
    widget.model.report_drive_status(
        [0xFFFF] * NUM_STRUT,
        [0xFFFF] * NUM_STRUT,
        [0xFFFFFFFF] * NUM_STRUT,
        [0xE0] * NUM_STRUT,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    struts = [f"strut_{idx}" for idx in range(NUM_STRUT)]

    for strut in struts:
        for idx, indicator in enumerate(widget._list_status_word[strut]):
            if idx == 3:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            elif idx == 5:
                assert indicator.palette().color(QPalette.Base) == Qt.gray
            elif idx in [6, 7, 8, 11, 13]:
                assert indicator.palette().color(QPalette.Base) == Qt.yellow
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

        for indicator in widget._list_latching_fault_status[strut]:
            assert indicator.palette().color(QPalette.Base) == Qt.red

        for idx, indicator in enumerate(widget._list_copley_status[strut]):
            if idx in [0, 1, 2, 3, 4, 5, 6, 9, 10, 18, 22, 28, 29, 30]:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            elif idx in [7, 8, 11, 12, 13, 16, 17, 19, 20, 21, 23, 24, 25]:
                assert indicator.palette().color(QPalette.Base) == Qt.yellow
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

        for idx, indicator in enumerate(widget._list_input_pin_state[strut]):
            if idx in [1, 2]:
                assert indicator.palette().color(QPalette.Base) == Qt.red
            else:
                assert indicator.palette().color(QPalette.Base) == Qt.green

    # Not triggered
    widget.model.report_drive_status(
        [0] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT, [0] * NUM_STRUT
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for strut in struts:
        assert (
            widget._list_status_word[strut][5].palette().color(QPalette.Base) == Qt.red
        )

        assert (
            widget._list_input_pin_state[strut][0].palette().color(QPalette.Base)
            == Qt.red
        )
