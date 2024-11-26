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
from lsst.ts.hexgui import Model
from lsst.ts.hexgui.tab import TabTelemetry
from lsst.ts.xml.enums import MTHexapod
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabTelemetry:
    widget = TabTelemetry(
        "Telemetry", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD)
    )
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabTelemetry) -> None:

    assert len(widget._application_status) == 15
