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

__all__ = ["TabTelemetry"]

from lsst.ts.guitool import (
    ButtonStatus,
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
    update_button_color,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QVBoxLayout

from ..constants import NUM_STRUT
from ..model import Model


class TabTelemetry(TabTemplate):
    """Table of the telemetry.

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

        self._telemetry_position = {
            "in_motion": create_label(),
            "position_x": create_label(),
            "position_y": create_label(),
            "position_z": create_label(),
            "position_rx": create_label(),
            "position_ry": create_label(),
            "position_rz": create_label(),
            "application_status_word": create_label(),
            "time_frame_difference": create_label(),
        }

        self._telemetry_strut = {
            "position_0": create_label(),
            "position_1": create_label(),
            "position_2": create_label(),
            "position_3": create_label(),
            "position_4": create_label(),
            "position_5": create_label(),
            "position_error_0": create_label(),
            "position_error_1": create_label(),
            "position_error_2": create_label(),
            "position_error_3": create_label(),
            "position_error_4": create_label(),
            "position_error_5": create_label(),
            "command_position_0": create_label(),
            "command_position_1": create_label(),
            "command_position_2": create_label(),
            "command_position_3": create_label(),
            "command_position_4": create_label(),
            "command_position_5": create_label(),
            "command_acceleration_0": create_label(),
            "command_acceleration_1": create_label(),
            "command_acceleration_2": create_label(),
            "command_acceleration_3": create_label(),
            "command_acceleration_4": create_label(),
            "command_acceleration_5": create_label(),
        }

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
            "drives_enabled": create_label(),
        }

        self._application_status = create_radio_indicators(15)

        self._set_default()

        self.set_widget_and_layout(is_scrollable=True)

    def create_layout(self) -> QVBoxLayout:

        layout_telemetry = QVBoxLayout()
        layout_telemetry.addWidget(self._create_group_position())
        layout_telemetry.addWidget(self._create_group_time())

        layout_control = QVBoxLayout()
        layout_control.addWidget(self._create_group_control_data())

        layout_configuration = QVBoxLayout()
        layout_configuration.addWidget(self._create_group_configuration())

        layout_application_status = QVBoxLayout()
        layout_application_status.addWidget(self._create_group_application_status())

        layout = QHBoxLayout()
        layout.addLayout(layout_telemetry)
        layout.addLayout(layout_control)
        layout.addLayout(layout_configuration)
        layout.addLayout(layout_application_status)

        return layout

    def _create_group_position(self) -> QGroupBox:
        """Create the group of position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("In motion:", self._telemetry_position["in_motion"])

        self.add_empty_row_to_form_layout(layout)

        for axis in ("x", "y", "z", "rx", "ry", "rz"):
            layout.addRow(
                f"Position {axis}:", self._telemetry_position[f"position_{axis}"]
            )

        self.add_empty_row_to_form_layout(layout)

        for idx in range(NUM_STRUT):
            layout.addRow(
                f"Strut position error {idx}:",
                self._telemetry_strut[f"position_error_{idx}"],
            )

        return create_group_box("Position", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

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

        layout.addRow("Drives enabled:", self._configuration["drives_enabled"])

        return create_group_box("Configuration Settings", layout)

    def _create_group_time(self) -> QGroupBox:
        """Create the group of time data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Time frame difference:", self._telemetry_position["time_frame_difference"]
        )

        return create_group_box("Time Data", layout)

    def _create_group_control_data(self) -> QGroupBox:
        """Create the group of control data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(NUM_STRUT):
            layout.addRow(
                f"Acceleration command {idx}:",
                self._telemetry_strut[f"command_acceleration_{idx}"],
            )

        self.add_empty_row_to_form_layout(layout)

        for idx in range(NUM_STRUT):
            layout.addRow(
                f"Position command {idx}:",
                self._telemetry_strut[f"command_position_{idx}"],
            )

        self.add_empty_row_to_form_layout(layout)

        for idx in range(NUM_STRUT):
            layout.addRow(f"Position {idx}:", self._telemetry_strut[f"position_{idx}"])

        return create_group_box("Strut Control Data", layout)

    def _create_group_application_status(self) -> QGroupBox:
        """Create the group of application status.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow(
            "Status word:", self._telemetry_position["application_status_word"]
        )
        self.add_empty_row_to_form_layout(layout)

        names = [
            "Following error",
            "Move complete",
            "GUI connected",
            "Relative move commanded",
            "Synchronous move",
            "Invalid command or value",
            "Safety interlock fault",
            "Extend limit switch",
            "Retract limit switch",
            "EtherCAT not ready",
            "Command source = CSC",
            "Motion timeout",
            "CSC connected",
            "Drive fault",
            "Simulink fault declared",
        ]
        for name, indicator in zip(names, self._application_status):
            layout.addRow(f"{name}:", indicator)

        return create_group_box("Application Status", layout)

    def _set_default(self) -> None:
        """Set the default values."""

        # Position telemetry
        self._telemetry_position["in_motion"].setText("False")

        for axis in ("x", "y", "z"):
            self._telemetry_position[f"position_{axis}"].setText("0 um")
            self._telemetry_position[f"position_r{axis}"].setText("0 deg")

        self._telemetry_position["application_status_word"].setText("0x0")

        self._telemetry_position["time_frame_difference"].setText("0 sec")

        # Strut telemetry
        for idx in range(NUM_STRUT):
            self._telemetry_strut[f"position_{idx}"].setText("0 um")
            self._telemetry_strut[f"position_error_{idx}"].setText("0 um")
            self._telemetry_strut[f"command_position_{idx}"].setText("0 um")
            self._telemetry_strut[f"command_acceleration_{idx}"].setText("0 um/sec^2")

        # Configuration
        self._configuration["position_max_xy"].setText("0 um")
        self._configuration["position_max_z"].setText("0 um")
        self._configuration["position_min_z"].setText("0 um")

        self._configuration["angle_max_xy"].setText("0 deg")
        self._configuration["angle_max_z"].setText("0 deg")
        self._configuration["angle_min_z"].setText("0 deg")

        self._configuration["linear_velocity_max_xy"].setText("0 um/sec")
        self._configuration["linear_velocity_max_z"].setText("0 um/sec")

        self._configuration["angular_velocity_max_xy"].setText("0 deg/sec")
        self._configuration["angular_velocity_max_z"].setText("0 deg/sec")

        self._configuration["strut_length_max"].setText("0 um")
        self._configuration["strut_velocity_max"].setText("0 um/sec")
        self._configuration["strut_acceleration_max"].setText("0 um/sec^2")

        self._configuration["drives_enabled"].setText("False")

        # Set the default indicators
        for indicator in self._application_status:
            update_button_color(indicator, QPalette.Base, ButtonStatus.Default)
