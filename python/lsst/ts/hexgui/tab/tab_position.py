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

__all__ = ["TabPosition"]

from PySide6.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from lsst.ts.guitool import FigureConstant, TabTemplate

from ..constants import NUM_DEGREE_OF_FREEDOM, NUM_STRUT
from ..model import Model
from ..signals import SignalPosition


class TabPosition(TabTemplate):
    """Table of the hexapod position.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    MIN_WIDTH = 150

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        # In micron
        self._strut_lengths = [0.0] * NUM_STRUT

        # (x, y, z, rx, ry, rz) in micron and degree
        self._positions = [0.0] * NUM_DEGREE_OF_FREEDOM

        # Realtime figures
        self._figures = self._create_figures()

        self.model = model

        # Timer to update the realtime figures
        self._timer = self.create_and_start_timer(self._callback_time_out, self.model.duration_refresh)

        self.set_widget_and_layout()

        self._set_signal_position(self.model.signals["position"])  # type: ignore[arg-type]

    def _create_figures(self, num_realtime: int = 200) -> dict:
        """Create the figures to show the positions of strut and hexapod.

        Parameters
        ----------
        num_realtime : `int`, optional
            Number of the realtime data (>=0). (the default is 200)

        Returns
        -------
        figures : `dict`
            Figures of the position and velocity.
        """

        figures = {
            "length": FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                "Length",
                "Strut Lengths (um)",
                legends=[f"Strut {idx}" for idx in range(NUM_STRUT)],
                num_lines=NUM_STRUT,
                is_realtime=True,
            ),
            "displacement": FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                "Displacement",
                "Hexapod Linear Displacement (um)",
                legends=["x", "y", "z"],
                num_lines=3,
                is_realtime=True,
            ),
            "angle": FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                "Angle",
                "Hexapod Angular Displacement (micro deg)",
                legends=["rx", "ry", "rz"],
                num_lines=3,
                is_realtime=True,
            ),
        }

        for figure in figures.values():
            figure.axis_x.setLabelFormat("%d")

        return figures

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the realtime figures."""

        for idx, strut_length in enumerate(self._strut_lengths):
            self._figures["length"].append_data(strut_length, idx)

        for idx, position in enumerate(self._positions):
            if idx < 3:
                self._figures["displacement"].append_data(position, idx)
            else:
                # Change to micro degree
                self._figures["angle"].append_data(position * 1e6, idx - 3)

        self.check_duration_and_restart_timer(self._timer, self.model.duration_refresh)

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        for figure in self._figures.values():
            figure.setMinimumWidth(self.MIN_WIDTH)
            layout.addWidget(figure)

        return layout

    def _set_signal_position(self, signal: SignalPosition) -> None:
        """Set the position signal.

        Parameters
        ----------
        signal : `SignalPosition`
            Signal.
        """

        signal.strut_position.connect(self._callback_strut_position)
        signal.hexapod_position.connect(self._callback_hexapod_position)

    @asyncSlot()
    async def _callback_strut_position(self, positions: list[float]) -> None:
        """Callback of the current strut position.

        Parameters
        ----------
        positions : `float`
            Strut positions of [strut_0, strut_1, ..., strut_5] in micron.
        """

        self._strut_lengths = positions

    @asyncSlot()
    async def _callback_hexapod_position(self, positions: list[float]) -> None:
        """Callback of the current hexapod position.

        Parameters
        ----------
        positions : `float`
            Hexapod positions of [x, y, z, rx, ry, rz] in micron and degree.
        """

        self._positions = positions
