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

__all__ = ["TabDriveStatus"]

from lsst.ts.guitool import (
    ButtonStatus,
    TabTemplate,
    create_group_box,
    create_radio_indicators,
    update_boolean_indicator_status,
    update_button_color,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..constants import NUM_STRUT
from ..model import Model
from ..signals import SignalDrive


class TabDriveStatus(TabTemplate):
    """Table of the drive status.

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

        # 16 bits
        self._list_status_word = self._create_indicators(16)

        # 16 bits
        self._list_latching_fault_status = self._create_indicators(16)

        # 32 bits
        self._list_copley_status = self._create_indicators(32)

        # Only 3 bits are used
        self._list_input_pin_state = self._create_indicators(3)

        self.set_widget_and_layout(is_scrollable=True)

        self._set_signal_drive(self.model.signals["drive"])  # type: ignore[arg-type]

    def _create_indicators(self, number: int) -> dict[str, list[QRadioButton]]:
        """Create the indicators for all struts.

        Parameters
        ----------
        number : `int`
            Number of the radio button indicator.

        Returns
        -------
        indicators : `dict` [`str`, `list` [`QRadioButton`]]
            Indicators. The keys are "strut_0", "strut_1", ..., "strut_5". The
            values are the list of radio button indicators.
        """

        keys = [f"strut_{idx}" for idx in range(NUM_STRUT)]

        indicators = dict()
        for key in keys:
            indicators[key] = create_radio_indicators(number)

        return indicators

    def create_layout(self) -> QVBoxLayout:

        # First column
        layout_drive = QVBoxLayout()
        layout_drive.addWidget(self._create_group_status_word())
        layout_drive.addWidget(self._create_group_latching_fault_status())

        # Second column
        layout_copley = QVBoxLayout()
        layout_copley.addWidget(self._create_group_copley_status())
        layout_copley.addWidget(self._create_group_input_pin_state())

        layout = QHBoxLayout()
        layout.addLayout(layout_drive)
        layout.addLayout(layout_copley)

        return layout

    def _create_group_status_word(self) -> QGroupBox:
        """Create the group box for the status word (0x6041).

        Returns
        -------
        `QGroupBox`
            Group box for the status word (0x6041).
        """

        names = [
            "Bit 0 - Ready to switch on:",
            "Bit 1 - Switched on:",
            "Bit 2 - Operation enabled:",
            "Bit 3 - Fault latched:",
            "Bit 4 - Voltage enabled:",
            "Bit 5 - Quick stop:",
            "Bit 6 - Switch on disabled:",
            "Bit 7 - Warning:",
            "Bit 8 - Last trajectory aborted:",
            "Bit 9 - Remote:",
            "Bit 10 - Target reached:",
            "Bit 11 - Internal limit active:",
            "Bit 12 - Set point acknowledge:",
            "Bit 13 - Following error:",
            "Bit 14 - Amplifier move status:",
            "Bit 15 - Reserved:",
        ]
        return create_group_box(
            "Status Word (0x6041)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [self._list_status_word[f"strut_{idx}"] for idx in range(NUM_STRUT)]
                ),
            ),
        )

    def _create_form_layout(
        self, names: list[str], items: list[QWidget | QLayout]
    ) -> QFormLayout:
        """Create a form layout.

        Parameters
        ----------
        names : `list` [`str`]
            Names.
        items : `list` [`QWidget` or `QLayout`]
            Items.

        Returns
        -------
        layout : `QFormLayout`
            Form layout.
        """

        layout = QFormLayout()
        for name, item in zip(names, items):
            layout.addRow(name, item)

        return layout

    def _combine_indicators(
        self, list_indicators: list[list[QRadioButton]]
    ) -> list[QHBoxLayout]:
        """Combine the indicators.

        Parameters
        ----------
        list_indicators : `list` [ `list` [`QRadioButton`] ]
            List of indicators.

        Returns
        -------
        combined_indicators : `list` [`QHBoxLayout`]
            Combined indicators.
        """

        combined_indicators = list()

        num_list = len(list_indicators)
        num_indicator_per_list = len(list_indicators[0])

        for idx_indicator in range(num_indicator_per_list):
            combined_indicator = QHBoxLayout()

            for idx_list in range(num_list):
                combined_indicator.addWidget(list_indicators[idx_list][idx_indicator])

            combined_indicators.append(combined_indicator)

        return combined_indicators

    def _create_group_latching_fault_status(self) -> QGroupBox:
        """Create the group box for the latching fault status (0x2183).

        Returns
        -------
        `QGroupBox`
            Group box for the latching fault status (0x2183).
        """

        names = [
            "Bit 0 - Data flash CRC failure:",
            "Bit 1 - Amplifier internal error:",
            "Bit 2 - Short circuit:",
            "Bit 3 - Amplifier over temperature:",
            "Bit 4 - Motor over temperature:",
            "Bit 5 - Over voltage:",
            "Bit 6 - Under voltage:",
            "Bit 7 - Feedback fault:",
            "Bit 8 - Phasing error:",
            "Bit 9 - Tracking error:",
            "Bit 10 - Over current:",
            "Bit 11 - FPGA failure 1:",
            "Bit 12 - Command input lost:",
            "Bit 13 - FPGA failure 2:",
            "Bit 14 - Safety circuit fault:",
            "Bit 15 - Unable to control current:",
        ]
        return create_group_box(
            "Latching Fault Status (0x2183)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_latching_fault_status[f"strut_{idx}"]
                        for idx in range(NUM_STRUT)
                    ]
                ),
            ),
        )

    def _create_group_copley_status(self) -> QGroupBox:
        """Create the group box for the Copley status (0x2180).

        Returns
        -------
        `QGroupBox`
            Group box for the Copley status (0x2180).
        """

        names = [
            "Bit 0 - Short circuit detected:",
            "Bit 1 - Amplifier over temperature:",
            "Bit 2 - Over voltage:",
            "Bit 3 - Under voltage:",
            "Bit 4 - Motor over temperature:",
            "Bit 5 - Feedback error:",
            "Bit 6 - Motor phasing error:",
            "Bit 7 - Current output limited:",
            "Bit 8 - Voltage output limited:",
            "Bit 9 - Retract limit switch active:",
            "Bit 10 - Extend limit switch active:",
            "Bit 11 - Enable input not active:",
            "Bit 12 - Amp is disabled by software:",
            "Bit 13 - Trying to stop motor:",
            "Bit 14 - Motor brake activated:",
            "Bit 15 - PWM outputs disabled:",
            "Bit 16 - Positive software limit condition:",
            "Bit 17 - Negative software limit condition:",
            "Bit 18 - Tracking error:",
            "Bit 19 - Tracking warning:",
            "Bit 20 - Amplifier in reset state:",
            "Bit 21 - Position counts wrapped:",
            "Bit 22 - Amplifier fault:",
            "Bit 23 - At velocity limit:",
            "Bit 24 - At acceleration limit:",
            "Bit 25 - Position error > tracking window:",
            "Bit 26 - Home switch is active:",
            "Bit 27 - In motion:",
            "Bit 28 - Velocity error > tracking window:",
            "Bit 29 - Phasing not set:",
            "Bit 30 - Command fault:",
            "Bit 31 - Not used:",
        ]
        return create_group_box(
            "Copley Status (0x2180)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_copley_status[f"strut_{idx}"]
                        for idx in range(NUM_STRUT)
                    ]
                ),
            ),
        )

    def _create_group_input_pin_state(self) -> QGroupBox:
        """Create the group box for the input pin state (0x219A).

        Returns
        -------
        `QGroupBox`
            Group box for the input pin state (0x219A).
        """

        names = [
            "Bit 6 - Safety interlock OK:",
            "Bit 7 - Extend limit switch hit:",
            "Bit 8 - Retract limit switch hit:",
        ]
        return create_group_box(
            "Input Pin State (0x219A)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_input_pin_state[f"strut_{idx}"]
                        for idx in range(NUM_STRUT)
                    ]
                ),
            ),
        )

    def _set_signal_drive(self, signal: SignalDrive) -> None:
        """Set the drive signal.

        Parameters
        ----------
        signal : `SignalDrive`
            Signal.
        """

        signal.status_word.connect(self._callback_status_word)
        signal.latching_fault.connect(self._callback_latching_fault)
        signal.copley_status.connect(self._callback_copley_status)
        signal.input_pin.connect(self._callback_input_pin)

    @asyncSlot()
    async def _callback_status_word(self, status_word: list[int]) -> None:
        """Callback of the status word.

        Parameters
        ----------
        status_word : `list` [`int`]
            Status word of [strut_0, strut_1, ..., strut_5].
        """

        faults = [3]
        warnings = [6, 7, 8, 11, 13]
        default_errors = [5]
        default_if_is_triggered = [5]
        for idx, status in enumerate(status_word):
            self._update_boolean_indicators(
                status,
                self._list_status_word[f"strut_{idx}"],
                faults,
                warnings,
                default_errors,
                default_if_is_triggered,
            )

    def _update_boolean_indicators(
        self,
        status: int,
        indicators: list[QRadioButton],
        faults: list[int],
        warnings: list[int],
        default_errors: list[int],
        default_if_is_triggered: list[int],
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
        warnings : `list` [`int`]
            Indexes of the warnings.
        default_errors : `list` [`int`]
            Default errors.
        default_if_is_triggered : `list` [`int`]
            Set the default status if the indicator is triggered.
        """

        for idx, indicator in enumerate(indicators):
            is_triggered = status & (1 << idx)
            update_boolean_indicator_status(
                indicator,
                is_triggered,
                is_fault=(idx in faults),
                is_warning=(idx in warnings),
                is_default_error=(idx in default_errors),
            )

            if (idx in default_if_is_triggered) and is_triggered:
                update_button_color(indicator, QPalette.Base, ButtonStatus.Default)

    @asyncSlot()
    async def _callback_latching_fault(self, latching_fault: list[int]) -> None:
        """Callback of the latching fault.

        Parameters
        ----------
        latching_fault : `list` [`int`]
            Latching fault status of [strut_0, strut_1, ..., strut_5].
        """

        faults = list(range(16))
        for idx, status in enumerate(latching_fault):
            self._update_boolean_indicators(
                status,
                self._list_latching_fault_status[f"strut_{idx}"],
                faults,
                [],
                [],
                [],
            )

    @asyncSlot()
    async def _callback_copley_status(self, copley_status: list[int]) -> None:
        """Callback of the Copley drive status.

        Parameters
        ----------
        copley_status : `list` [`int`]
            Copley drive status of [strut_0, strut_1, ..., strut_5].
        """

        faults = [0, 1, 2, 3, 4, 5, 6, 9, 10, 18, 22, 28, 29, 30]
        warnings = [7, 8, 11, 12, 13, 16, 17, 19, 20, 21, 23, 24, 25]
        for idx, status in enumerate(copley_status):
            self._update_boolean_indicators(
                status,
                self._list_copley_status[f"strut_{idx}"],
                faults,
                warnings,
                [],
                [],
            )

    @asyncSlot()
    async def _callback_input_pin(self, input_pin: list[int]) -> None:
        """Callback of the input pin status.

        Parameters
        ----------
        input_pin : `list` [`int`]
            Input pin status of [strut_0, strut_1, ..., strut_5].
        """

        bit_offset = 5

        faults = [1, 2]
        default_errors = [0]
        for idx, status in enumerate(input_pin):
            self._update_boolean_indicators(
                status >> bit_offset,
                self._list_input_pin_state[f"strut_{idx}"],
                faults,
                [],
                default_errors,
                [],
            )
