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

__all__ = ["TabConfig"]

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QGroupBox, QVBoxLayout
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalConfig
from ..structs import Config


class TabConfig(TabTemplate):
    """Table of the configuration.

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

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        self.model = model

        self._configuration = {
            "position_max_xy": create_label(),
            "position_max_z": create_label(),
            "position_min_z": create_label(),
            "angle_max_xy": create_label(),
            "angle_max_z": create_label(),
            "angle_min_z": create_label(),
            "linear_velocity_max_xy": create_label(),
            "linear_velocity_max_z": create_label(),
            "angular_velocity_max_xy": create_label(),
            "angular_velocity_max_z": create_label(),
            "strut_length_max": create_label(),
            "strut_velocity_max": create_label(),
            "strut_acceleration_max": create_label(),
            "pivot_x": create_label(),
            "pivot_y": create_label(),
            "pivot_z": create_label(),
            "drives_enabled": create_label(),
        }

        self.set_widget_and_layout()

        self._set_signal_config(self.model.signals["config"])  # type: ignore[arg-type]

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_configuration())

        return layout

    def _create_group_configuration(self) -> QGroupBox:
        """Create the group of configuration.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Position maximum xy:", self._configuration["position_max_xy"])
        layout.addRow("Position maximum z:", self._configuration["position_max_z"])
        layout.addRow("Position minimum z:", self._configuration["position_min_z"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Angle maximum xy:", self._configuration["angle_max_xy"])
        layout.addRow("Angle maximum z:", self._configuration["angle_max_z"])
        layout.addRow("Angle minimum z:", self._configuration["angle_min_z"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow(
            "Linear velocity maximum xy:", self._configuration["linear_velocity_max_xy"]
        )
        layout.addRow(
            "Linear velocity maximum z:", self._configuration["linear_velocity_max_z"]
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow(
            "Angular velocity maximum xy:",
            self._configuration["angular_velocity_max_xy"],
        )
        layout.addRow(
            "Angular velocity maximum z:", self._configuration["angular_velocity_max_z"]
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Strut length maximum:", self._configuration["strut_length_max"])
        layout.addRow(
            "Strut velocity maximum:", self._configuration["strut_velocity_max"]
        )
        layout.addRow(
            "Strut acceleration maximum:", self._configuration["strut_acceleration_max"]
        )

        self.add_empty_row_to_form_layout(layout)

        for axis in ["x", "y", "z"]:
            layout.addRow(f"Pivot {axis}:", self._configuration[f"pivot_{axis}"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Drives enabled:", self._configuration["drives_enabled"])

        return create_group_box("Configuration Settings", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def _set_signal_config(self, signal: SignalConfig) -> None:
        """Set the config signal.

        Parameters
        ----------
        signal : `SignalConfig`
            Signal.
        """

        signal.config.connect(self._callback_config)

    @asyncSlot()
    async def _callback_config(self, config: Config) -> None:
        """Callback of the configuration.

        Parameters
        ----------
        config : `Config`
            Configuration.
        """

        self._configuration["position_max_xy"].setText(f"{config.pos_limits[0]:.2f} um")
        self._configuration["position_min_z"].setText(f"{config.pos_limits[1]:.2f} um")
        self._configuration["position_max_z"].setText(f"{config.pos_limits[2]:.2f} um")

        self._configuration["angle_max_xy"].setText(f"{config.pos_limits[3]:.6f} deg")
        self._configuration["angle_min_z"].setText(f"{config.pos_limits[4]:.6f} deg")
        self._configuration["angle_max_z"].setText(f"{config.pos_limits[5]:.6f} deg")

        self._configuration["linear_velocity_max_xy"].setText(
            f"{config.vel_limits[0]:.2f} um/sec"
        )
        self._configuration["linear_velocity_max_z"].setText(
            f"{config.vel_limits[1]:.2f} um/sec"
        )

        self._configuration["angular_velocity_max_xy"].setText(
            f"{config.vel_limits[2]:.6f} deg/sec"
        )
        self._configuration["angular_velocity_max_z"].setText(
            f"{config.vel_limits[3]:.6f} deg/sec"
        )

        self._configuration["strut_length_max"].setText(
            f"{config.max_displacement_strut:.2f} um"
        )
        self._configuration["strut_velocity_max"].setText(
            f"{config.max_velocity_strut:.2f} um/sec"
        )
        self._configuration["strut_acceleration_max"].setText(
            f"{config.acceleration_strut:.2f} um/sec^2"
        )

        self._configuration["pivot_x"].setText(f"{config.pivot[0]:.2f} um")
        self._configuration["pivot_y"].setText(f"{config.pivot[1]:.2f} um")
        self._configuration["pivot_z"].setText(f"{config.pivot[2]:.2f} um")

        color = Qt.green if config.drives_enabled else Qt.red
        self._configuration["drives_enabled"].setText(
            f"<font color='{color.name}'>{str(config.drives_enabled)}</font>"
        )
