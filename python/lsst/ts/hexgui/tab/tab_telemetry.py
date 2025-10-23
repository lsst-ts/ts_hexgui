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
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
    update_boolean_indicator_status,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..constants import NUM_STRUT
from ..model import Model
from ..signals import (
    SignalApplicationStatus,
    SignalControl,
    SignalPosition,
    SignalPower,
)


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
            "current_0": create_label(),
            "current_1": create_label(),
            "current_2": create_label(),
            "current_3": create_label(),
            "current_4": create_label(),
            "current_5": create_label(),
        }

        self._application_status = create_radio_indicators(15)

        self.set_widget_and_layout()

        self._set_signal_application_status(
            self.model.signals["application_status"]  # type: ignore[arg-type]
        )
        self._set_signal_control(
            self.model.signals["control"]  # type: ignore[arg-type]
        )
        self._set_signal_position(
            self.model.signals["position"]  # type: ignore[arg-type]
        )
        self._set_signal_power(self.model.signals["power"])  # type: ignore[arg-type]

    def create_layout(self) -> QVBoxLayout:
        layout_telemetry = QVBoxLayout()
        layout_telemetry.addWidget(self._create_group_position())
        layout_telemetry.addWidget(self._create_group_power())

        layout_control = QVBoxLayout()
        layout_control.addWidget(self._create_group_control_data())

        layout_application_status = QVBoxLayout()
        layout_application_status.addWidget(self._create_group_time())
        layout_application_status.addWidget(self._create_group_application_status())

        layout = QHBoxLayout()
        layout.addLayout(layout_telemetry)
        layout.addLayout(layout_control)
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
            layout.addRow(f"Position {axis}:", self._telemetry_position[f"position_{axis}"])

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

    def _create_group_time(self) -> QGroupBox:
        """Create the group of time data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Time frame difference:", self._telemetry_position["time_frame_difference"])

        return create_group_box("Time Data", layout)

    def _create_group_power(self) -> QGroupBox:
        """Create the group of power data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        for idx in range(NUM_STRUT):
            layout.addRow(f"Current {idx}:", self._telemetry_strut[f"current_{idx}"])

        return create_group_box("Power", layout)

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

        layout.addRow("Status word:", self._telemetry_position["application_status_word"])
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

    def _set_signal_application_status(self, signal: SignalApplicationStatus) -> None:
        """Set the application status signal.

        Parameters
        ----------
        signal : `SignalApplicationStatus`
            Signal.
        """

        signal.status.connect(self._callback_application_status)

    @asyncSlot()
    async def _callback_application_status(self, status: int) -> None:
        """Callback of the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        self._update_application_status(status)

    def _update_application_status(self, status: int) -> None:
        """Update the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        self._telemetry_position["application_status_word"].setText(hex(status))

        faults = [0, 5, 6, 7, 8, 9, 11, 13, 14]
        self._update_boolean_indicators(status, self._application_status, faults)

    def _update_boolean_indicators(
        self, status: int, indicators: list[QRadioButton], faults: list[int]
    ) -> None:
        """Update the boolean indicators.

        Parameters
        ----------
        status : `int`
            Status.
        indicators : `list` [`QRadioButton`]
            Indicators.
        faults : `list` [`int`]
            Indexes of the faults.
        """

        for idx, indicator in enumerate(indicators):
            update_boolean_indicator_status(
                indicator,
                status & (1 << idx),
                is_fault=(idx in faults),
            )

    def _set_signal_control(self, signal: SignalControl) -> None:
        """Set the control signal.

        Parameters
        ----------
        signal : `SignalControl`
            Signal.
        """

        signal.command_acceleration.connect(self._callback_command_acceleration)
        signal.command_position.connect(self._callback_command_position)
        signal.time_difference.connect(self._callback_time_difference)

    @asyncSlot()
    async def _callback_command_acceleration(self, accelerations: list[float]) -> None:
        """Callback of the commanded acceleration.

        Parameters
        ----------
        accelerations : `list` [`float`]
            Commanded accelerations of [strut_0, strut_1, ..., strut_5] in
            um/sec^2.
        """

        for idx, acceleration in enumerate(accelerations):
            self._telemetry_strut[f"command_acceleration_{idx}"].setText(f"{acceleration:.3f} um/sec^2")

    @asyncSlot()
    async def _callback_command_position(self, positions: list[float]) -> None:
        """Callback of the commanded position.

        Parameters
        ----------
        positions : `list` [`float`]
            Commanded positions of [strut_0, strut_1, ..., strut_5] in um.
        """

        for idx, position in enumerate(positions):
            self._telemetry_strut[f"command_position_{idx}"].setText(f"{position:.3f} um")

    @asyncSlot()
    async def _callback_time_difference(self, time_difference: float) -> None:
        """Callback of the time frame difference.

        Parameters
        ----------
        time_difference : `float`
            Time difference in seconds.
        """

        self._telemetry_position["time_frame_difference"].setText(f"{time_difference:.7f} sec")

    def _set_signal_position(self, signal: SignalPosition) -> None:
        """Set the position signal.

        Parameters
        ----------
        signal : `SignalPosition`
            Signal.
        """

        signal.strut_position.connect(self._callback_strut_position)
        signal.strut_position_error.connect(self._callback_strut_position_error)
        signal.hexapod_position.connect(self._callback_hexapod_position)
        signal.in_motion.connect(self._callback_in_motion)

    @asyncSlot()
    async def _callback_strut_position(self, positions: list[float]) -> None:
        """Callback of the current strut position.

        Parameters
        ----------
        positions : `list` [`float`]
            Strut positions of [strut_0, strut_1, ..., strut_5] in micron.
        """

        for idx, position in enumerate(positions):
            self._telemetry_strut[f"position_{idx}"].setText(f"{position:.3f} um")

    @asyncSlot()
    async def _callback_strut_position_error(self, position_errors: list[float]) -> None:
        """Callback of the current strut position error.

        Parameters
        ----------
        position_errors : `list` [`float`]
            Strut position errors of [strut_0, strut_1, ..., strut_5] in
            micron.
        """

        for idx, position_error in enumerate(position_errors):
            self._telemetry_strut[f"position_error_{idx}"].setText(f"{position_error:.3f} um")

    @asyncSlot()
    async def _callback_hexapod_position(self, positions: list[float]) -> None:
        """Callback of the current hexapod position.

        Parameters
        ----------
        positions : `list` [`float`]
            Hexapod positions of [x, y, z, rx, ry, rz] in micron and degree.
        """

        for idx, axis in enumerate(["x", "y", "z"]):
            self._telemetry_position[f"position_{axis}"].setText(f"{positions[idx]:.3f} um")
            self._telemetry_position[f"position_r{axis}"].setText(f"{positions[idx + 3]:.7f} deg")

    @asyncSlot()
    async def _callback_in_motion(self, in_motion: bool) -> None:
        """Callback of the in-motion flag.

        Parameters
        ----------
        in_motion : `bool`
            Hexapod is in motion or not.
        """

        color = Qt.green if in_motion else Qt.black
        self._telemetry_position["in_motion"].setText(f"<font color='{color.name}'>{str(in_motion)}</font>")

    def _set_signal_power(self, signal: SignalPower) -> None:
        """Set the power signal.

        Parameters
        ----------
        signal : `SignalPower`
            Signal.
        """

        signal.current.connect(self._callback_current)

    @asyncSlot()
    async def _callback_current(self, currents: list[float]) -> None:
        """Callback of the current.

        Parameters
        ----------
        currents : `list` [`float`]
            Currents of [strut_0, strut_1, ..., strut_5] in ampere.
        """

        for idx in range(NUM_STRUT):
            self._telemetry_strut[f"current_{idx}"].setText(f"{currents[idx]:.6f} A")
