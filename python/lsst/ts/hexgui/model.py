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

__all__ = ["Model"]

import logging
import typing

from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import Signal

from .config import Config
from .constants import NUM_DEGREE_OF_FREEDOM, NUM_STRUT
from .enums import CommandSource
from .signals import (
    SignalApplicationStatus,
    SignalConfig,
    SignalControl,
    SignalDrive,
    SignalPosition,
    SignalPower,
    SignalState,
)
from .status import Status


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    hexapod_type : `MTHexapod.SalIndex`
        The hexapod type.
    host : `str`, optional
        Host address. (the default is "localhost")
    port : `int`, optional
        Port to connect. (the default is 5560)
    timeout_connection : `float`, optional
        Connection timeout in second. (the default is 10.0)
    is_simulation_mode : `bool`, optional
        True if running in simulation mode. (the default is False)
    duration_refresh : `int`, optional
        Duration to refresh the data in milliseconds. (the default is 100)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    hexapod_type : `MTHexapod.SalIndex`
        The hexapod type.
    connection_information : `dict`
        TCP/IP connection information.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    """

    def __init__(
        self,
        log: logging.Logger,
        hexapod_type: MTHexapod.SalIndex,
        host: str = "localhost",
        port: int = 5560,
        timeout_connection: float = 10.0,
        is_simulation_mode: bool = False,
        duration_refresh: int = 100,
    ) -> None:

        self.log = log
        self.hexapod_type = hexapod_type

        self.connection_information = {
            "host": host,
            "port": port,
            "timeout_connection": timeout_connection,
        }

        self._is_simulation_mode = is_simulation_mode
        self.duration_refresh = duration_refresh

        self._status = Status()

        self.signals = {
            "state": SignalState(),
            "application_status": SignalApplicationStatus(),
            "drive": SignalDrive(),
            "config": SignalConfig(),
            "control": SignalControl(),
            "position": SignalPosition(),
            "power": SignalPower(),
        }

    def report_default(self) -> None:
        """Report the default status."""

        signal_state = self.signals["state"]
        signal_state.command_source.emit(  # type: ignore[attr-defined]
            CommandSource.GUI.value
        )
        signal_state.state.emit(  # type: ignore[attr-defined]
            MTHexapod.ControllerState.STANDBY.value
        )
        signal_state.substate_enabled.emit(  # type: ignore[attr-defined]
            MTHexapod.EnabledSubstate.STATIONARY.value
        )

        signal_drive = self.signals["drive"]
        signal_drive.status_word.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.latching_fault.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.copley_status.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.input_pin.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]

        signal_application_status = self.signals["application_status"]
        signal_application_status.status.emit(0)  # type: ignore[attr-defined]

        self.report_config(Config())
        self.report_control_data([0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0)
        self.report_position(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_DEGREE_OF_FREEDOM, False
        )

    def report_config(self, config: Config) -> None:
        """Report the configuration.

        Parameters
        ----------
        config : `Config`
            Configuration details.
        """

        self.signals["config"].config.emit(config)  # type: ignore[attr-defined]

    def report_control_data(
        self,
        command_acceleration: list[float],
        command_position: list[float],
        time_difference: float,
    ) -> None:
        """Report the control data.

        Parameters
        ----------
        command_acceleration : `list` [`float`]
            Commanded accelerations of [strut_0, strut_1, ..., strut_5] in
            um/sec^2.
        command_position : `list` [`float`]
            Commanded positions of [strut_0, strut_1, ..., strut_5] in um.
        time_difference : `float`
            Time frame difference in seconds.
        """

        signal = self.signals["control"]
        signal.command_acceleration.emit(command_acceleration)  # type: ignore[attr-defined]
        signal.command_position.emit(command_position)  # type: ignore[attr-defined]
        signal.time_difference.emit(time_difference)  # type: ignore[attr-defined]

    def report_position(
        self,
        strut_position: list[float],
        strut_position_error: list[float],
        hexapod_position: list[float],
        in_motion: bool,
    ) -> None:
        """Report the position.

        Parameters
        ----------
        strut_position : `list` [`float`]
            Strut positions of [strut_0, strut_1, ..., strut_5] in micron.
        strut_position_error : list` [`float`]
            Strut position errors of [strut_0, strut_1, ..., strut_5] in
            micron.
        hexapod_position : list` [`float`]
            Hexapod positions of [x, y, z, rx, ry, rz] in micron and degree.
        in_motion : `bool`
            Hexapod is in motion or not.
        """

        signal = self.signals["position"]
        signal.strut_position.emit(strut_position)  # type: ignore[attr-defined]
        signal.strut_position_error.emit(strut_position_error)  # type: ignore[attr-defined]
        signal.hexapod_position.emit(hexapod_position)  # type: ignore[attr-defined]
        signal.in_motion.emit(in_motion)  # type: ignore[attr-defined]

    def report_power(self, current: list[float], voltage: list[float]) -> None:
        """Report the power.

        Parameters
        ----------
        current : `list` [`float`]
            Currents of [strut_0, strut_1, ..., strut_5] in ampere.
        voltage : `list` [`float`]
            Bus voltages of [drive_0, drive_1, drive_2] in volts.
        """

        signal = self.signals["power"]
        signal.current.emit(current)  # type: ignore[attr-defined]
        signal.voltage.emit(voltage)  # type: ignore[attr-defined]

    def report_state(
        self,
        command_source: CommandSource,
        state: MTHexapod.ControllerState,
        substate_enabled: MTHexapod.EnabledSubstate,
    ) -> None:
        """Report the controller's state.

        Parameters
        ----------
        command_source : enum `CommandSource`
            Command source.
        state : enum `MTHexapod.ControllerState`
            State.
        substate_enabled : enum `MTHexapod.EnabledSubstate`
            Enabled substate.
        """

        signal = self.signals["state"]

        self._compare_status_and_report(
            "command_source",
            command_source.value,
            signal.command_source,  # type: ignore[attr-defined]
        )
        self._compare_status_and_report("state", state.value, signal.state)  # type: ignore[attr-defined]
        self._compare_status_and_report(
            "substate_enabled", substate_enabled.value, signal.substate_enabled  # type: ignore[attr-defined]
        )

    def _compare_status_and_report(
        self, field: str, value: typing.Any, signal: Signal
    ) -> None:
        """Compare the value with current status and report it if different.

        Parameters
        ----------
        field : `str`
            Field of the status.
        value : `typing.Any`
            Value.
        signal : `PySide6.QtCore.Signal`
            Signal.

        Raises
        ------
        `TypeError`
            When the type of value does not match with the type of status's
            value.
        """

        status_value = getattr(self._status, field)
        if type(value) is not type(status_value):
            raise TypeError(
                f"Type of value ({type(value)}) does not match with type of "
                f"status's value ({type(status_value)})."
            )

        if value != status_value:
            signal.emit(value)
            setattr(self._status, field, value)

    def report_application_status(self, status: int) -> None:
        """Report the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        signal = self.signals["application_status"]

        self._compare_status_and_report(
            "application_status", status, signal.status  # type: ignore[attr-defined]
        )

    def report_drive_status(
        self,
        status_word: list[int],
        latching_fault: list[int],
        copley_status: list[int],
        input_pin: list[int],
    ) -> None:
        """Report the drive status.

        Parameters
        ----------
        status_word : `list` [`int`]
            Status word of [strut_0, strut_1, ..., strut_5].
        latching_fault : `list` [`int`]
            Latching fault status of [strut_0, strut_1, ..., strut_5].
        copley_status : `list` [`int`]
            Copley drive status of [strut_0, strut_1, ..., strut_5].
        input_pin : `list` [`int`]
            Input pin status of [strut_0, strut_1, ..., strut_5].
        """

        signal = self.signals["drive"]

        self._compare_status_and_report(
            "status_word", status_word, signal.status_word  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "latching_fault", latching_fault, signal.latching_fault  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "copley_status", copley_status, signal.copley_status  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "input_pin", input_pin, signal.input_pin  # type: ignore[attr-defined]
        )
