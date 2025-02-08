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

__all__ = ["ControlPanel"]

import asyncio

from lsst.ts.guitool import (
    ButtonStatus,
    QMessageBoxAsync,
    create_double_spin_box,
    create_group_box,
    create_label,
    run_command,
    set_button,
    update_button_color,
)
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from .constants import (
    CAM_UV_MAX_DEG,
    CAM_W_MAX_DEG,
    CAM_W_MIN_DEG,
    CAM_XY_MAX_MIC,
    CAM_Z_MAX_MIC,
    CAM_Z_MIN_MIC,
    M2_UV_MAX_DEG,
    M2_W_MAX_DEG,
    M2_W_MIN_DEG,
    M2_XY_MAX_MIC,
    M2_Z_MAX_MIC,
    M2_Z_MIN_MIC,
    MAX_ACCEL_LIMIT,
    MAX_ACTUATOR_RANGE_MIC,
    MAX_ANGULAR_VEL_LIMIT,
    MAX_LINEAR_VEL_LIMIT,
    MAX_PIVOT_X_MIC,
    MAX_PIVOT_Y_MIC,
    MAX_PIVOT_Z_MIC,
    NUM_STRUT,
)
from .enums import (
    CommandCode,
    CommandSource,
    MotionPattern,
    TriggerEnabledSubState,
    TriggerState,
)
from .model import Model
from .signals import SignalConfig, SignalState
from .structs import Config


class ControlPanel(QWidget):
    """Control panel.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide6.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model: Model) -> None:
        super().__init__()

        self.model = model

        self._indicators = self._create_indicators()
        self._labels = {
            "source": create_label(),
            "state": create_label(),
            "enabled_substate": create_label(),
        }

        self._command_parameters = self._create_command_parameters()
        self._commands = self._create_commands()

        self._button_command = set_button(
            "Send Command",
            self._callback_send_command,
            tool_tip="Send the command to the controller.",
        )

        self.setLayout(self._create_layout())

        self._set_signal_state(self.model.signals["state"])  # type: ignore[arg-type]
        self._set_signal_config(self.model.signals["config"])  # type: ignore[arg-type]

        self._set_default()

    def _create_indicators(self) -> dict:
        """Create the indicators.

        Returns
        -------
        `dict`
            Indicators.
        """

        return {
            "fault": set_button(
                "",
                None,
                is_indicator=True,
                tool_tip="System is faulted or not.",
            ),
            "drive": set_button(
                "",
                None,
                is_indicator=True,
                tool_tip="Drive is on or not.",
            ),
        }

    def _create_command_parameters(
        self,
        decimal_displacement: int = 2,
        decimal_angle: int = 4,
    ) -> dict:
        """Create the command parameters.

        Parameters
        ----------
        decimal_displacement : `int`, optional
            Decimal of the displacement. (the default is 2)
        decimal_angle : `int`, optional
            Decimal of the angle. (the default is 4)

        Returns
        -------
        `dict`
            Command parameters.
        """

        state = QComboBox()
        for trigger in TriggerState:
            state.addItem(trigger.name)

        enabled_substate = QComboBox()
        for substate in TriggerEnabledSubState:
            enabled_substate.addItem(substate.name)

        if self.model.hexapod_type == MTHexapod.SalIndex.CAMERA_HEXAPOD:
            max_x = CAM_XY_MAX_MIC
            min_x = -CAM_XY_MAX_MIC

            max_y = CAM_XY_MAX_MIC
            min_y = -CAM_XY_MAX_MIC

            max_z = CAM_Z_MAX_MIC
            min_z = CAM_Z_MIN_MIC

            max_rx = CAM_UV_MAX_DEG
            min_rx = -CAM_UV_MAX_DEG

            max_ry = CAM_UV_MAX_DEG
            min_ry = -CAM_UV_MAX_DEG

            max_rz = CAM_W_MAX_DEG
            min_rz = CAM_W_MIN_DEG

        else:
            max_x = M2_XY_MAX_MIC
            min_x = -M2_XY_MAX_MIC

            max_y = M2_XY_MAX_MIC
            min_y = -M2_XY_MAX_MIC

            max_z = M2_Z_MAX_MIC
            min_z = M2_Z_MIN_MIC

            max_rx = M2_UV_MAX_DEG
            min_rx = -M2_UV_MAX_DEG

            max_ry = M2_UV_MAX_DEG
            min_ry = -M2_UV_MAX_DEG

            max_rz = M2_W_MAX_DEG
            min_rz = M2_W_MIN_DEG

        position_x = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=max_x,
            minimum=min_x,
        )
        position_y = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=max_y,
            minimum=min_y,
        )
        position_z = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=max_z,
            minimum=min_z,
        )

        position_rx = create_double_spin_box(
            "deg",
            decimal_angle,
            maximum=max_rx,
            minimum=min_rx,
        )
        position_ry = create_double_spin_box(
            "deg",
            decimal_angle,
            maximum=max_ry,
            minimum=min_ry,
        )
        position_rz = create_double_spin_box(
            "deg",
            decimal_angle,
            maximum=max_rz,
            minimum=min_rz,
        )

        strut_0 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )
        strut_1 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )
        strut_2 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )
        strut_3 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )
        strut_4 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )
        strut_5 = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_ACTUATOR_RANGE_MIC,
            minimum=-MAX_ACTUATOR_RANGE_MIC,
        )

        pivot_x = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_PIVOT_X_MIC,
            minimum=-MAX_PIVOT_X_MIC,
        )
        pivot_y = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_PIVOT_Y_MIC,
            minimum=-MAX_PIVOT_Y_MIC,
        )
        pivot_z = create_double_spin_box(
            "um",
            decimal_displacement,
            maximum=MAX_PIVOT_Z_MIC,
            minimum=-MAX_PIVOT_Z_MIC,
        )

        linear_velocity_xy = create_double_spin_box(
            "um/sec",
            decimal_displacement,
            maximum=MAX_LINEAR_VEL_LIMIT,
        )
        linear_velocity_z = create_double_spin_box(
            "um/sec",
            decimal_displacement,
            maximum=MAX_LINEAR_VEL_LIMIT,
        )
        angular_velocity_rxry = create_double_spin_box(
            "deg/sec",
            decimal_angle,
            maximum=MAX_ANGULAR_VEL_LIMIT,
        )
        angular_velocity_rz = create_double_spin_box(
            "deg/sec",
            decimal_angle,
            maximum=MAX_ANGULAR_VEL_LIMIT,
        )

        acceleration = create_double_spin_box(
            "um/sec^2",
            decimal_displacement,
            maximum=MAX_ACCEL_LIMIT,
        )

        motion_pattern = QComboBox()
        for pattern in MotionPattern:
            motion_pattern.addItem(pattern.name)

        command_source = QComboBox()
        for source in CommandSource:
            command_source.addItem(source.name)

        return {
            "state": state,
            "enabled_substate": enabled_substate,
            "position_x": position_x,
            "position_y": position_y,
            "position_z": position_z,
            "position_rx": position_rx,
            "position_ry": position_ry,
            "position_rz": position_rz,
            "strut_0": strut_0,
            "strut_1": strut_1,
            "strut_2": strut_2,
            "strut_3": strut_3,
            "strut_4": strut_4,
            "strut_5": strut_5,
            "pivot_x": pivot_x,
            "pivot_y": pivot_y,
            "pivot_z": pivot_z,
            "linear_velocity_xy": linear_velocity_xy,
            "linear_velocity_z": linear_velocity_z,
            "angular_velocity_rxry": angular_velocity_rxry,
            "angular_velocity_rz": angular_velocity_rz,
            "acceleration": acceleration,
            "motion_pattern": motion_pattern,
            "source": command_source,
        }

    def _create_commands(self) -> dict:
        """Create the commands.

        Returns
        -------
        `dict`
            Commands. The key is the name of the command and the value is the
            button.
        """

        command_state = QRadioButton("State command", parent=self)
        command_enabled_substate = QRadioButton(
            "Enabled sub-state command", parent=self
        )
        command_set_position = QRadioButton("Set position", parent=self)
        command_set_position_offset = QRadioButton("Set position offset", parent=self)
        command_set_position_raw = QRadioButton("Set raw position", parent=self)
        command_set_pivot = QRadioButton("Set pivot", parent=self)
        command_commander = QRadioButton("Switch command source", parent=self)
        command_mask = QRadioButton("Mask limit switch", parent=self)
        command_config_velocity = QRadioButton("Configure velocity", parent=self)
        command_config_acceleration = QRadioButton(
            "Configure acceleration", parent=self
        )

        command_state.setToolTip("Transition the state.")
        command_enabled_substate.setToolTip("Transition the enabled sub-state.")
        command_set_position.setToolTip("Set the hexapod position.")
        command_set_position_offset.setToolTip("Set the hexapod position offset.")
        command_set_position_raw.setToolTip("Set the hexapod raw position (struts).")
        command_set_pivot.setToolTip("Set the hexapod pivot position.")
        command_commander.setToolTip("Switch the command source (GUI or CSC).")
        command_mask.setToolTip("Temporarily mask the limit switches.")
        command_config_velocity.setToolTip(
            "Configure the maximum velocity for position and orientation."
        )
        command_config_acceleration.setToolTip(
            "Configure the maximum acceleration for all struts."
        )

        command_state.toggled.connect(self._callback_command)
        command_enabled_substate.toggled.connect(self._callback_command)
        command_set_position.toggled.connect(self._callback_command)
        command_set_position_offset.toggled.connect(self._callback_command)
        command_set_position_raw.toggled.connect(self._callback_command)
        command_set_pivot.toggled.connect(self._callback_command)
        command_commander.toggled.connect(self._callback_command)
        command_mask.toggled.connect(self._callback_command)
        command_config_velocity.toggled.connect(self._callback_command)
        command_config_acceleration.toggled.connect(self._callback_command)

        return {
            "state": command_state,
            "enabled_substate": command_enabled_substate,
            "position": command_set_position,
            "position_offset": command_set_position_offset,
            "position_raw": command_set_position_raw,
            "pivot": command_set_pivot,
            "commander": command_commander,
            "mask": command_mask,
            "config_velocity": command_config_velocity,
            "config_acceleration": command_config_acceleration,
        }

    @asyncSlot()
    async def _callback_command(self) -> None:
        """Callback of the command button."""

        parameters_position = [
            "position_x",
            "position_y",
            "position_z",
            "position_rx",
            "position_ry",
            "position_rz",
            "motion_pattern",
        ]

        if self._commands["state"].isChecked():
            self._enable_command_parameters(["state"])

        elif self._commands["enabled_substate"].isChecked():
            self._enable_command_parameters(["enabled_substate"])

        elif self._commands["position"].isChecked():
            self._enable_command_parameters(parameters_position)

        elif self._commands["position_offset"].isChecked():
            self._enable_command_parameters(parameters_position)

        elif self._commands["position_raw"].isChecked():
            self._enable_command_parameters(
                [
                    "strut_0",
                    "strut_1",
                    "strut_2",
                    "strut_3",
                    "strut_4",
                    "strut_5",
                    "motion_pattern",
                ]
            )

        elif self._commands["pivot"].isChecked():
            self._enable_command_parameters(
                [
                    "pivot_x",
                    "pivot_y",
                    "pivot_z",
                ]
            )

        elif self._commands["commander"].isChecked():
            self._enable_command_parameters(["source"])

        elif self._commands["mask"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["config_velocity"].isChecked():
            self._enable_command_parameters(
                [
                    "linear_velocity_xy",
                    "linear_velocity_z",
                    "angular_velocity_rxry",
                    "angular_velocity_rz",
                ]
            )

        elif self._commands["config_acceleration"].isChecked():
            self._enable_command_parameters(["acceleration"])

    def _enable_command_parameters(self, enabled_parameters: list[str]) -> None:
        """Enable the command parameters.

        Parameters
        ----------
        enabled_parameters : `list` [`str`]
            Enabled command parameters.
        """

        for name, value in self._command_parameters.items():
            value.setEnabled(name in enabled_parameters)

    @asyncSlot()
    async def _callback_send_command(self) -> None:
        """Callback of the send-command button to command the controller."""

        # Check the dangerous commands
        if await self._check_dangerous_commands():
            return

        # Check the connection status
        if not await run_command(self.model.assert_is_connected):
            return

        # Check the selected command
        name = self._get_selected_command()

        self.model.log.info(f"Send the command: {name}.")

        # Command the controller
        match name:
            case "state":
                trigger_state = TriggerState(
                    self._command_parameters["state"].currentIndex()
                )
                command = self.model.make_command_state(trigger_state)

            case "enabled_substate":
                command = self.model.make_command_enabled_substate(
                    TriggerEnabledSubState(
                        self._command_parameters["enabled_substate"].currentIndex()
                    ),
                    self._get_motion_pattern(),
                )

            case "position":
                command = self.model.make_command(
                    CommandCode.POSITION_SET,
                    param1=self._command_parameters["position_x"].value(),
                    param2=self._command_parameters["position_y"].value(),
                    param3=self._command_parameters["position_z"].value(),
                    param4=self._command_parameters["position_rx"].value(),
                    param5=self._command_parameters["position_ry"].value(),
                    param6=self._command_parameters["position_rz"].value(),
                )

            case "position_offset":
                command = self.model.make_command(
                    CommandCode.POSITION_OFFSET,
                    param1=self._command_parameters["position_x"].value(),
                    param2=self._command_parameters["position_y"].value(),
                    param3=self._command_parameters["position_z"].value(),
                    param4=self._command_parameters["position_rx"].value(),
                    param5=self._command_parameters["position_ry"].value(),
                    param6=self._command_parameters["position_rz"].value(),
                )

            case "position_raw":
                command = self.model.make_command(
                    CommandCode.SET_RAW_STRUT,
                    param1=self._command_parameters["strut_0"].value(),
                    param2=self._command_parameters["strut_1"].value(),
                    param3=self._command_parameters["strut_2"].value(),
                    param4=self._command_parameters["strut_3"].value(),
                    param5=self._command_parameters["strut_4"].value(),
                    param6=self._command_parameters["strut_5"].value(),
                )

            case "pivot":
                command = self.model.make_command(
                    CommandCode.SET_PIVOT_POINT,
                    param1=self._command_parameters["pivot_x"].value(),
                    param2=self._command_parameters["pivot_y"].value(),
                    param3=self._command_parameters["pivot_z"].value(),
                )

            case "commander":
                command = self.model.make_command(
                    CommandCode.CMD_SOURCE,
                    param1=float(
                        CommandSource(
                            self._command_parameters["source"].currentIndex()
                        ).value
                    ),
                )

            case "mask":
                command = self.model.make_command(CommandCode.MASK_LIMIT_SW)

            case "config_velocity":
                command = self.model.make_command(
                    CommandCode.CONFIG_VEL,
                    param1=self._command_parameters["linear_velocity_xy"].value(),
                    param2=self._command_parameters["angular_velocity_rxry"].value(),
                    param3=self._command_parameters["linear_velocity_z"].value(),
                    param4=self._command_parameters["angular_velocity_rz"].value(),
                )

            case "config_acceleration":
                command = self.model.make_command(
                    CommandCode.CONFIG_ACCEL,
                    param1=self._command_parameters["acceleration"].value(),
                )

            case _:
                # Should not reach here
                command = self.model.make_command(CommandCode.DEFAULT)
                self.model.log.error(f"Unknown command: {name}.")

        # Workaround the mypy check
        assert self.model.client is not None

        # For the state related command, there is some special thing to do.
        if name == "state":
            if trigger_state == TriggerState.Enable:
                # Turn on the drives
                await run_command(self.model.enable_drives, True)

            elif trigger_state == TriggerState.ClearError:
                # Clear twice in total
                await run_command(self.model.client.run_command, command)
                await asyncio.sleep(1.0)

        # Send the command
        await run_command(self.model.client.run_command, command)

        # Turn off the drives when needed
        if name == "state":
            if trigger_state == TriggerState.StandBy:
                await run_command(self.model.enable_drives, False)

    async def _check_dangerous_commands(self) -> bool:
        """Check the dangerous commands.

        Returns
        -------
        `bool`
            True if the dangerous command is selected and the user wants to
            give up. False otherwise.
        """

        motion_pattern = self._get_motion_pattern()

        dialog = None
        if self._commands["position_raw"].isChecked():
            dialog = self._create_dialog_warning("Raw position command")

        elif motion_pattern == MotionPattern.Async:
            dialog = self._create_dialog_warning("Asynchronous motion")

        if dialog is not None:
            result = await dialog.show()

            if result == QMessageBoxAsync.Cancel:
                return True

        return False

    def _get_motion_pattern(self) -> MotionPattern:
        """Get the motion pattern.

        Returns
        -------
        `MotionPattern`
            Motion pattern.
        """

        return MotionPattern(self._command_parameters["motion_pattern"].currentIndex())

    def _create_dialog_warning(self, title: str) -> QMessageBoxAsync:
        """Create the warning dialog.

        Parameters
        ----------
        title : `str`
            Title of the dialog.

        Returns
        -------
        dialog : `lsst.ts.guitool.QMessageBoxAsync`
            Disconnect dialog.
        """

        dialog = QMessageBoxAsync()
        dialog.setIcon(QMessageBoxAsync.Warning)
        dialog.setWindowTitle(title)

        dialog.setText(
            "This may result in the damage to flexures. and should be used "
            "only by qualified operators.\n\n"
            "Do you want to continue the command?"
        )

        dialog.addButton(QMessageBoxAsync.Ok)
        dialog.addButton(QMessageBoxAsync.Cancel)

        # Block the user to interact with other running widgets
        dialog.setModal(True)

        return dialog

    def _get_selected_command(self) -> str:
        """Get the selected command.

        Returns
        -------
        name : `str`
            Selected command.
        """

        for name, commmand in self._commands.items():
            if commmand.isChecked():
                return name

        return ""

    def _create_layout(self) -> QVBoxLayout:
        """Set the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_summary())
        layout.addWidget(self._create_group_commands())

        return layout

    def _create_group_summary(self) -> QGroupBox:
        """Create the group of summary.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Fault Status:", self._indicators["fault"])
        layout.addRow("Drive Status:", self._indicators["drive"])
        layout.addRow("Command Source:", self._labels["source"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("State:", self._labels["state"])
        layout.addRow("Enabled Sub-State:", self._labels["enabled_substate"])

        return create_group_box("Summary", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def _create_group_commands(self) -> QGroupBox:
        """Create the group of commands.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_commands = QHBoxLayout()
        layout_commands.addWidget(self._create_group_command_name())
        layout_commands.addWidget(self._create_group_command_parameters())

        layout = QVBoxLayout()
        layout.addLayout(layout_commands)
        layout.addWidget(self._button_command)

        return create_group_box("Commands", layout)

    def _create_group_command_name(self) -> QGroupBox:
        """Create the group of command name.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        for command in self._commands.values():
            layout.addWidget(command)

        return create_group_box("Command", layout)

    def _create_group_command_parameters(self) -> QGroupBox:
        """Create the group of command parameters.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        # Column 1
        layout_parameters_1 = QFormLayout()
        layout_parameters_1.addRow("State trigger:", self._command_parameters["state"])
        layout_parameters_1.addRow(
            "Enabled sub-state trigger:", self._command_parameters["enabled_substate"]
        )
        layout_parameters_1.addRow(
            "Command source:", self._command_parameters["source"]
        )
        layout_parameters_1.addRow(
            "Motion pattern:", self._command_parameters["motion_pattern"]
        )
        for axis in ["X", "Y", "Z"]:
            layout_parameters_1.addRow(
                f"Pivot {axis}:",
                self._command_parameters[f"pivot_{axis.lower()}"],
            )

        # Column 2
        layout_parameters_2 = QFormLayout()
        for axis in ["X", "Y", "Z", "Rx", "Ry", "Rz"]:
            layout_parameters_2.addRow(
                f"{axis}:",
                self._command_parameters[f"position_{axis.lower()}"],
            )

        # Column 3
        layout_parameters_3 = QFormLayout()
        for idx in range(NUM_STRUT):
            layout_parameters_3.addRow(
                f"Strut {idx}:",
                self._command_parameters[f"strut_{idx}"],
            )

        # Column 4
        layout_parameters_4 = QFormLayout()
        layout_parameters_4.addRow(
            "XY:", self._command_parameters["linear_velocity_xy"]
        )
        layout_parameters_4.addRow("Z:", self._command_parameters["linear_velocity_z"])
        layout_parameters_4.addRow(
            "RxRy:", self._command_parameters["angular_velocity_rxry"]
        )
        layout_parameters_4.addRow(
            "Rz:", self._command_parameters["angular_velocity_rz"]
        )
        layout_parameters_4.addRow(
            "Acceleration:", self._command_parameters["acceleration"]
        )

        layout = QHBoxLayout()
        layout.addLayout(layout_parameters_1)
        layout.addLayout(layout_parameters_2)
        layout.addLayout(layout_parameters_3)
        layout.addLayout(layout_parameters_4)

        return create_group_box("Command Parameters", layout)

    def _set_signal_state(self, signal: SignalState) -> None:
        """Set the state signal.

        Parameters
        ----------
        signal : `SignalState`
            Signal.
        """

        signal.command_source.connect(self._callback_command_source)
        signal.state.connect(self._callback_state)
        signal.substate_enabled.connect(self._callback_substate_enabled)

    @asyncSlot()
    async def _callback_command_source(self, source: int) -> None:
        """Callback of the controller's command source signal.

        Parameters
        ----------
        source : `int`
            Source.
        """

        self._labels["source"].setText(CommandSource(source).name)

    @asyncSlot()
    async def _callback_state(self, state: int) -> None:
        """Callback of the controller's state signal.

        Parameters
        ----------
        state : `int`
            State.
        """

        controller_state = MTHexapod.ControllerState(state)
        self._labels["state"].setText(controller_state.name)

        self._update_fault_status(controller_state == MTHexapod.ControllerState.FAULT)

    def _update_fault_status(self, is_fault: bool) -> None:
        """Update the fault status.

        Parameters
        ----------
        is_fault : `bool`
            Is fault or not.
        """

        # Set the text
        text = "Faulted" if is_fault else "Not Faulted"
        self._indicators["fault"].setText(text)

        # Set the color
        status = ButtonStatus.Error if is_fault else ButtonStatus.Normal
        update_button_color(self._indicators["fault"], QPalette.Button, status)

    @asyncSlot()
    async def _callback_substate_enabled(self, substate: int) -> None:
        """Callback of the controller's enabled substate signal.

        Parameters
        ----------
        substate : `int`
            Substate.
        """

        self._labels["enabled_substate"].setText(
            MTHexapod.EnabledSubstate(substate).name
        )

    def _set_default(self) -> None:
        """Set the default values."""

        self._commands["state"].setChecked(True)

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

        for idx, axis in enumerate(["x", "y", "z"]):
            self._command_parameters[f"pivot_{axis}"].setValue(config.pivot[idx])

        self._update_drive_status(config.drives_enabled)

        self._command_parameters["linear_velocity_xy"].setValue(config.vel_limits[0])
        self._command_parameters["linear_velocity_z"].setValue(config.vel_limits[1])
        self._command_parameters["angular_velocity_rxry"].setValue(config.vel_limits[2])
        self._command_parameters["angular_velocity_rz"].setValue(config.vel_limits[3])

        self._command_parameters["acceleration"].setValue(config.acceleration_strut)

    def _update_drive_status(self, is_on: bool) -> None:
        """Update the drive status.

        Parameters
        ----------
        is_on : `bool`
            Is on or not.
        """

        # Set the text
        text = "On" if is_on else "Off"
        self._indicators["drive"].setText(text)

        # Set the color
        status = ButtonStatus.Normal if is_on else ButtonStatus.Default
        update_button_color(self._indicators["drive"], QPalette.Button, status)
