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
from lsst.ts.hexgui import Config, Model
from lsst.ts.hexgui.tab import TabConfig
from lsst.ts.xml.enums import MTHexapod
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabConfig:
    widget = TabConfig("Config", Model(logging.getLogger(), MTHexapod.SalIndex.CAMERA_HEXAPOD))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_set_signal_config(widget: TabConfig) -> None:
    config = Config()
    config.acceleration_strut = 1.1

    for idx, value in enumerate([2.2, 3.3, 4.4, 5.5]):
        config.vel_limits[idx] = value

    config.max_displacement_strut = 6.6
    config.max_velocity_strut = 7.7

    for idx, value in enumerate([8.8, 9.9, 10.1, 11.1, 12.2, 13.3]):
        config.pos_limits[idx] = value

    for idx, value in enumerate([14.4, 15.5, 16.6]):
        config.pivot[idx] = value

    config.drives_enabled = True

    widget.model.report_config(config)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._configuration["position_max_xy"].text() == "8.80 um"
    assert widget._configuration["position_max_z"].text() == "10.10 um"
    assert widget._configuration["position_min_z"].text() == "9.90 um"
    assert widget._configuration["angle_max_xy"].text() == "11.100000 deg"
    assert widget._configuration["angle_max_z"].text() == "13.300000 deg"
    assert widget._configuration["angle_min_z"].text() == "12.200000 deg"
    assert widget._configuration["linear_velocity_max_xy"].text() == "2.20 um/sec"
    assert widget._configuration["linear_velocity_max_z"].text() == "3.30 um/sec"
    assert widget._configuration["angular_velocity_max_xy"].text() == "4.400000 deg/sec"
    assert widget._configuration["angular_velocity_max_z"].text() == "5.500000 deg/sec"
    assert widget._configuration["strut_length_max"].text() == "6.60 um"
    assert widget._configuration["strut_velocity_max"].text() == "7.70 um/sec"
    assert widget._configuration["strut_acceleration_max"].text() == "1.10 um/sec^2"
    assert widget._configuration["pivot_x"].text() == "14.40 um"
    assert widget._configuration["pivot_y"].text() == "15.50 um"
    assert widget._configuration["pivot_z"].text() == "16.60 um"
    assert widget._configuration["drives_enabled"].text() == "<font color='green'>True</font>"
